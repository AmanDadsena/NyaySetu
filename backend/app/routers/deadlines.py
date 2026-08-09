"""
Saved deadlines.

The calculator answers a question once. This is what keeps the answer alive:
a signed-in user pins a deadline to a matter of their own, and it counts down.

A digest endpoint reports what is falling due so an external scheduler — a cron
job, a GitHub Action — can send reminders. Delivery itself is deliberately not
implemented: it needs SMTP credentials the project does not have, and a mail
path that silently fails is worse than none, because the user believes they
will be warned.
"""

from __future__ import annotations

from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import SavedDeadline, User
from app.middleware import get_current_user
from app.tools import limitation

router = APIRouter(prefix="/api/deadlines", tags=["deadlines"])


class DeadlineCreate(BaseModel):
    rule_id: str
    event_date: date
    matter_reference: str | None = Field(default=None, max_length=120)
    notes: str | None = None


class DeadlineUpdate(BaseModel):
    matter_reference: str | None = None
    notes: str | None = None
    completed: bool | None = None


class DeadlineOut(BaseModel):
    id: int
    rule_id: str
    rule_label: str
    citation: str | None
    matter_reference: str | None
    event_date: date
    deadline_date: date
    notes: str | None
    completed: bool
    days_remaining: int
    expired: bool
    urgency: str


def _to_out(row: SavedDeadline, today: date) -> DeadlineOut:
    remaining = (row.deadline_date - today).days
    expired = remaining < 0

    if row.completed:
        urgency = "done"
    elif expired:
        urgency = "expired"
    elif remaining <= 7:
        urgency = "urgent"
    elif remaining <= 30:
        urgency = "soon"
    else:
        urgency = "comfortable"

    return DeadlineOut(
        id=row.id,
        rule_id=row.rule_id,
        rule_label=row.rule_label,
        citation=row.citation,
        matter_reference=row.matter_reference,
        event_date=row.event_date,
        deadline_date=row.deadline_date,
        notes=row.notes,
        completed=row.completed,
        days_remaining=remaining,
        expired=expired,
        urgency=urgency,
    )


@router.post("", response_model=DeadlineOut)
async def save_deadline(
    payload: DeadlineCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DeadlineOut:
    try:
        computed = limitation.calculate(payload.rule_id, payload.event_date)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    if not computed.has_limitation or not computed.deadline:
        raise HTTPException(
            status_code=400,
            detail="That matter has no limitation period, so there is no deadline to track.",
        )

    row = SavedDeadline(
        user_id=current_user.id,
        rule_id=payload.rule_id,
        rule_label=computed.label,
        citation=computed.citation,
        matter_reference=(payload.matter_reference or "").strip() or None,
        event_date=payload.event_date,
        deadline_date=date.fromisoformat(computed.deadline),
        notes=(payload.notes or "").strip() or None,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return _to_out(row, date.today())


@router.get("", response_model=list[DeadlineOut])
async def list_deadlines(
    include_completed: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[DeadlineOut]:
    query = select(SavedDeadline).where(SavedDeadline.user_id == current_user.id)
    if not include_completed:
        query = query.where(SavedDeadline.completed.is_(False))

    result = await db.execute(query.order_by(SavedDeadline.deadline_date.asc()))
    today = date.today()
    return [_to_out(row, today) for row in result.scalars().all()]


@router.patch("/{deadline_id}", response_model=DeadlineOut)
async def update_deadline(
    deadline_id: int,
    payload: DeadlineUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DeadlineOut:
    result = await db.execute(
        select(SavedDeadline).where(
            SavedDeadline.id == deadline_id,
            SavedDeadline.user_id == current_user.id,
        )
    )
    row = result.scalars().first()
    if row is None:
        raise HTTPException(status_code=404, detail="Deadline not found")

    if payload.matter_reference is not None:
        row.matter_reference = payload.matter_reference.strip() or None
    if payload.notes is not None:
        row.notes = payload.notes.strip() or None
    if payload.completed is not None:
        row.completed = payload.completed

    await db.commit()
    await db.refresh(row)
    return _to_out(row, date.today())


@router.delete("/{deadline_id}")
async def delete_deadline(
    deadline_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    result = await db.execute(
        select(SavedDeadline).where(
            SavedDeadline.id == deadline_id,
            SavedDeadline.user_id == current_user.id,
        )
    )
    row = result.scalars().first()
    if row is None:
        raise HTTPException(status_code=404, detail="Deadline not found")

    await db.delete(row)
    await db.commit()
    return {"status": "deleted", "id": deadline_id}


@router.get("/digest")
async def digest(
    within_days: int = Query(default=7, ge=1, le=90),
    mark_notified: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Deadlines falling due within `within_days`, plus anything already overdue.

    Intended for a scheduler to poll and turn into a reminder. Pass
    `mark_notified=true` once a reminder has actually been delivered, so the
    next run does not repeat it.
    """
    today = date.today()
    result = await db.execute(
        select(SavedDeadline).where(
            SavedDeadline.user_id == current_user.id,
            SavedDeadline.completed.is_(False),
        ).order_by(SavedDeadline.deadline_date.asc())
    )
    rows = result.scalars().all()

    due = [r for r in rows if (r.deadline_date - today).days <= within_days]

    if mark_notified and due:
        now = datetime.now(timezone.utc)
        for row in due:
            row.last_notified_at = now
        await db.commit()

    return {
        "generated_at": today.isoformat(),
        "within_days": within_days,
        "overdue": [_to_out(r, today).model_dump() for r in due if r.deadline_date < today],
        "upcoming": [_to_out(r, today).model_dump() for r in due if r.deadline_date >= today],
    }
