"""
Structured legal tools: limitation deadlines, forum routing, document drafting.

None of these calls a model. They are lookup tables and calendar arithmetic, so
they answer in microseconds, work with no network, and give the same answer
twice — which is what you want from something that tells a person whether they
still have the right to sue.
"""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.tools import documents, fees, forum, limitation, timeline

router = APIRouter(prefix="/api/tools", tags=["tools"])


# ── Limitation ──────────────────────────────────────────────────────────
class LimitationRequest(BaseModel):
    rule_id: str
    event_date: date = Field(description="When the clock started — see the rule's trigger")


@router.get("/limitation")
async def list_limitation_rules() -> dict:
    return {"rules": limitation.catalogue()}


@router.post("/limitation")
async def compute_limitation(request: LimitationRequest) -> dict:
    try:
        result = limitation.calculate(request.rule_id, request.event_date)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    if request.event_date > date.today():
        raise HTTPException(
            status_code=400,
            detail="That date is in the future. Enter the date the event actually happened.",
        )

    return result.__dict__


# ── Forum ───────────────────────────────────────────────────────────────
class ForumRequest(BaseModel):
    rule_id: str
    claim_value: float | None = Field(
        default=None,
        description="Amount paid for the goods or service, where the forum depends on it",
    )


@router.get("/forum")
async def list_forum_rules() -> dict:
    return {"rules": forum.catalogue()}


@router.post("/forum")
async def route_forum(request: ForumRequest) -> dict:
    try:
        result = forum.route(request.rule_id, request.claim_value)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return result.__dict__


# ── Documents ───────────────────────────────────────────────────────────
class DocumentRequest(BaseModel):
    template_id: str
    data: dict = Field(default_factory=dict)


@router.get("/documents")
async def list_templates() -> dict:
    return {"templates": documents.catalogue()}


@router.post("/documents")
async def generate_document(request: DocumentRequest) -> dict:
    try:
        result = documents.generate(request.template_id, request.data)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return result.__dict__


# ── Case timeline ───────────────────────────────────────────────────────
class TimelineRequest(BaseModel):
    matter_id: str
    start_date: date
    known: dict[str, str] = Field(
        default_factory=dict,
        description="Optional dates for downstream anchors, keyed by anchor name",
    )


@router.get("/timeline")
async def list_matter_types() -> dict:
    return {"matters": timeline.catalogue()}


@router.post("/timeline")
async def build_timeline(request: TimelineRequest) -> dict:
    try:
        result = timeline.build(request.matter_id, request.start_date, request.known)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {
        "matter_id": result.matter_id,
        "label": result.label,
        "start_label": result.start_label,
        "start_date": result.start_date,
        "entries": [e.__dict__ for e in result.entries],
        "related": result.related,
    }


# ── Court fees ──────────────────────────────────────────────────────────
class FeeRequest(BaseModel):
    matter: str
    value: float = 0.0
    state: str | None = None


@router.get("/fees")
async def list_fee_matters() -> dict:
    return fees.catalogue()


@router.post("/fees")
async def compute_fee(request: FeeRequest) -> dict:
    try:
        result = fees.calculate(request.matter, request.value, request.state)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return result.__dict__
