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

from app.tools import (
    citations,
    documents,
    fees,
    forum,
    holidays,
    limitation,
    maintenance,
    stamp_duty,
    timeline,
)

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


# ── Citations ───────────────────────────────────────────────────────────
class CitationRequest(BaseModel):
    text: str = Field(min_length=20, description="Judgment, brief or opinion text")


@router.post("/citations")
async def extract_citations(request: CitationRequest) -> dict:
    result = citations.extract(request.text)
    return {
        "word_count": result.word_count,
        "cases": [c.__dict__ for c in result.cases],
        "statutes": [c.__dict__ for c in result.statutes],
        "unresolved": result.unresolved,
    }


# ── Stamp duty ──────────────────────────────────────────────────────────
class StampDutyRequest(BaseModel):
    instrument: str
    value: float = 0.0
    circle_rate: float = Field(
        default=0.0,
        description="Circle rate / ready reckoner value. Duty runs on whichever "
                    "of this and the consideration is higher.",
    )
    state: str | None = None
    buyer: str = Field(default="man", description="man | woman | joint")


@router.get("/stamp-duty")
async def list_instruments() -> dict:
    return stamp_duty.catalogue()


@router.post("/stamp-duty")
async def compute_stamp_duty(request: StampDutyRequest) -> dict:
    try:
        result = stamp_duty.calculate(
            request.instrument,
            request.value,
            request.circle_rate,
            request.state,
            request.buyer,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return result.__dict__


# ── Maintenance ─────────────────────────────────────────────────────────
class MaintenanceRequest(BaseModel):
    payer_income: float = Field(ge=0, description="Respondent's net monthly income")
    claimant_income: float = Field(default=0.0, ge=0)
    spouse: bool = True
    children: int = Field(default=0, ge=0, le=20)
    parents: int = Field(default=0, ge=0, le=2)


@router.get("/maintenance")
async def maintenance_reference() -> dict:
    return maintenance.catalogue()


@router.post("/maintenance")
async def estimate_maintenance(request: MaintenanceRequest) -> dict:
    if not (request.spouse or request.children or request.parents):
        raise HTTPException(
            status_code=400,
            detail="Select at least one person the maintenance is claimed for.",
        )
    result = maintenance.calculate(
        request.payer_income,
        request.claimant_income,
        request.spouse,
        request.children,
        request.parents,
    )
    return result.__dict__


# ── Working days ────────────────────────────────────────────────────────
@router.get("/calendar")
async def calendar_status() -> dict:
    return holidays.calendar_status()
