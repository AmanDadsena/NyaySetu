"""
Limitation calculator.

Limitation is where people lose cases they would have won. The right expires
quietly, nobody tells you, and by the time a lawyer looks at it the answer is
"you should have come last year". Section 3 of the Limitation Act, 1963 requires
a court to dismiss a time-barred suit *even if the other side never raises it*.

So this is deliberately deterministic — no model, no retrieval, no judgement
call. Dates in, dates out, with the provision that governs them.

Two things the arithmetic must get right:

  * Section 12(1) excludes the day from which the period runs, so a three-year
    period starting 10 March 2022 expires on 10 March 2025, not 9 March.
  * Where the last day is a court holiday, Section 4 lets you file on the next
    working day. That is resolved exactly against the calendar in
    `holidays.py`, and the result says how confident it is: a deployment that
    has not supplied its court's notified list only knows about weekends and
    the fixed national holidays.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta

from . import holidays


@dataclass(frozen=True)
class LimitationRule:
    id: str
    label: str
    #: What starts the clock. Shown to the user, because picking the wrong
    #: start date is the most common way this goes wrong.
    trigger: str
    days: int | None = None
    months: int | None = None
    years: int | None = None
    act: str = ""
    section: str = ""
    #: Whether a court can excuse delay, and on what basis.
    condonable: bool = False
    condonation_note: str = ""
    notes: tuple[str, ...] = ()
    #: Passage ids in the RAG corpus that explain the underlying right.
    related: tuple[str, ...] = ()
    category: str = "General"


RULES: list[LimitationRule] = [
    # ── Consumer ────────────────────────────────────────────────────────
    LimitationRule(
        id="consumer_complaint",
        label="Consumer complaint (defective goods or deficient service)",
        trigger="the date the cause of action arose — usually when the defect appeared or the service failed",
        years=2,
        act="Consumer Protection Act, 2019",
        section="Section 69",
        condonable=True,
        condonation_note=(
            "The Commission may admit a late complaint if you satisfy it there was "
            "sufficient cause for the delay, and it must record its reasons."
        ),
        notes=(
            "A continuing wrong gives a fresh cause of action each day it continues.",
            "Time spent pursuing the company's own grievance process still counts — "
            "do not wait indefinitely for them to respond.",
        ),
        related=("consumer_where_to_file", "consumer_how_to_file"),
        category="Consumer",
    ),
    LimitationRule(
        id="consumer_appeal_state",
        label="Appeal from a District Consumer Commission order",
        trigger="the date of the order",
        days=45,
        act="Consumer Protection Act, 2019",
        section="Section 41",
        condonable=True,
        condonation_note="Delay may be condoned on sufficient cause.",
        notes=("An appellant who was ordered to pay must deposit 50% of the amount first.",),
        related=("consumer_where_to_file",),
        category="Consumer",
    ),

    # ── Cheque bounce: a chain where every link is fatal ─────────────────
    LimitationRule(
        id="cheque_notice",
        label="Cheque bounce — sending the demand notice",
        trigger="the date you received the bank's dishonour memo",
        days=30,
        act="Negotiable Instruments Act, 1881",
        section="Section 138(b)",
        condonable=False,
        notes=(
            "This one cannot be extended. Miss it and the offence is not made out, "
            "though you can still sue civilly to recover the money.",
            "The cheque itself must have been presented within three months of its date.",
        ),
        related=("cheque_bounce",),
        category="Money recovery",
    ),
    LimitationRule(
        id="cheque_complaint",
        label="Cheque bounce — filing the complaint",
        trigger="the date the drawer's 15-day payment window expired",
        days=30,
        act="Negotiable Instruments Act, 1881",
        section="Section 142(b)",
        condonable=True,
        condonation_note=(
            "The Magistrate may take a late complaint if you show sufficient cause "
            "for not filing in time."
        ),
        notes=(
            "The 15 days run from when the drawer received your notice, not when you sent it.",
            "File where the bank branch that returned the cheque is located.",
        ),
        related=("cheque_bounce",),
        category="Money recovery",
    ),

    # ── Civil suits ─────────────────────────────────────────────────────
    LimitationRule(
        id="suit_money",
        label="Suit to recover money or enforce a contract",
        trigger="the date the money became due, or the contract was broken",
        years=3,
        act="Limitation Act, 1963",
        section="Schedule, Articles 18–55",
        condonable=False,
        notes=(
            "A written, signed acknowledgement of the debt before the period expires "
            "restarts the three years from the date of that acknowledgement (Section 18).",
            "A part payment recorded in the debtor's own hand has the same effect (Section 19).",
        ),
        related=("contract_essentials", "limitation_periods"),
        category="Civil",
    ),
    LimitationRule(
        id="suit_immovable_possession",
        label="Suit for possession of immovable property",
        trigger="the date the defendant's possession became adverse to you",
        years=12,
        act="Limitation Act, 1963",
        section="Schedule, Article 65",
        condonable=False,
        notes=(
            "Once twelve years pass, you do not merely lose the remedy — your title "
            "itself is extinguished under Section 27. This is the one limitation "
            "period that destroys the right rather than just barring the suit.",
        ),
        related=("property_registration",),
        category="Property",
    ),
    LimitationRule(
        id="tort_compensation",
        label="Suit for compensation (injury, negligence, wrongful act)",
        trigger="the date the wrongful act was committed or the injury occurred",
        years=3,
        act="Limitation Act, 1963",
        section="Schedule, Articles 72–91",
        condonable=False,
        related=("limitation_periods",),
        category="Civil",
    ),
    LimitationRule(
        id="defamation",
        label="Suit for defamation",
        trigger="the date the defamatory statement was published",
        years=1,
        act="Limitation Act, 1963",
        section="Schedule, Articles 75–76",
        condonable=False,
        notes=("One year, not three — defamation is the short outlier among civil wrongs.",),
        related=("defamation",),
        category="Civil",
    ),
    LimitationRule(
        id="execution_decree",
        label="Executing a decree you have already won",
        trigger="the date of the decree, or the date it became enforceable",
        years=12,
        act="Limitation Act, 1963",
        section="Schedule, Article 136",
        condonable=False,
        notes=("Winning is not collecting. A decree unexecuted for twelve years is worthless.",),
        category="Civil",
    ),

    # ── Appeals ─────────────────────────────────────────────────────────
    LimitationRule(
        id="appeal_district",
        label="Appeal to a District Court from a decree",
        trigger="the date of the decree",
        days=30,
        act="Limitation Act, 1963",
        section="Schedule, Article 116",
        condonable=True,
        condonation_note="Section 5 allows condonation on sufficient cause.",
        notes=("Time taken to obtain a certified copy of the decree is excluded (Section 12(2)).",),
        category="Appeals",
    ),
    LimitationRule(
        id="appeal_high_court",
        label="Appeal to a High Court from a decree",
        trigger="the date of the decree",
        days=90,
        act="Limitation Act, 1963",
        section="Schedule, Article 116",
        condonable=True,
        condonation_note="Section 5 allows condonation on sufficient cause.",
        notes=("Time taken to obtain a certified copy of the decree is excluded (Section 12(2)).",),
        category="Appeals",
    ),
    LimitationRule(
        id="arbitration_challenge",
        label="Challenging an arbitral award",
        trigger="the date you received the signed award",
        months=3,
        act="Arbitration and Conciliation Act, 1996",
        section="Section 34(3)",
        condonable=True,
        condonation_note=(
            "A further 30 days only, on sufficient cause — and not one day beyond. "
            "Section 5 of the Limitation Act does not rescue you here."
        ),
        notes=("This is the strictest deadline in Indian civil practice. Treat it as absolute.",),
        category="Appeals",
    ),

    # ── Transparency ────────────────────────────────────────────────────
    LimitationRule(
        id="rti_first_appeal",
        label="RTI first appeal",
        trigger="the date you received the reply, or the date the 30-day reply period expired",
        days=30,
        act="Right to Information Act, 2005",
        section="Section 19(1)",
        condonable=True,
        condonation_note="The Appellate Authority may admit a late appeal on sufficient cause.",
        notes=("No fee is payable for either appeal.",),
        related=("rti_appeals", "rti_how_to_file"),
        category="Transparency",
    ),
    LimitationRule(
        id="rti_second_appeal",
        label="RTI second appeal to the Information Commission",
        trigger="the date of the first appellate order, or the date it was due",
        days=90,
        act="Right to Information Act, 2005",
        section="Section 19(3)",
        condonable=True,
        condonation_note="The Commission may admit a late appeal on sufficient cause.",
        related=("rti_appeals",),
        category="Transparency",
    ),

    # ── Work ────────────────────────────────────────────────────────────
    LimitationRule(
        id="wages_claim",
        label="Claim for unpaid wages",
        trigger="the date the wages fell due",
        years=3,
        act="Code on Wages, 2019",
        section="Section 45(4)",
        condonable=True,
        condonation_note="The authority may admit a late claim on sufficient cause.",
        notes=("Three years — considerably longer than the one year under the old Payment of Wages Act.",),
        related=("wage_theft",),
        category="Work",
    ),
    LimitationRule(
        id="posh_complaint",
        label="Sexual harassment complaint to the Internal Committee",
        trigger="the date of the incident, or the last incident in a series",
        months=3,
        act="Sexual Harassment of Women at Workplace Act, 2013",
        section="Section 9(1)",
        condonable=True,
        condonation_note=(
            "The Committee may extend by a further three months if satisfied that "
            "circumstances prevented you from filing in time, and must record why."
        ),
        related=("vishaka_posh",),
        category="Work",
    ),
    LimitationRule(
        id="gratuity_application",
        label="Applying for gratuity",
        trigger="the date gratuity became payable",
        days=30,
        act="Payment of Gratuity Act, 1972",
        section="Rule 7",
        condonable=True,
        condonation_note=(
            "A late application must still be accepted if sufficient cause is shown — "
            "the employer cannot refuse purely on delay."
        ),
        notes=("The employer must pay within 30 days of it becoming due, whether or not you apply.",),
        related=("gratuity",),
        category="Work",
    ),

    # ── No limitation — as important to say ─────────────────────────────
    LimitationRule(
        id="mact_claim",
        label="Motor accident compensation claim",
        trigger="the date of the accident",
        days=None,
        act="Motor Vehicles Act, 1988",
        section="Section 166(3), omitted by the 2019 amendment",
        condonable=False,
        notes=(
            "There is no limitation period. The six-month bar was removed by the 2019 "
            "amendment. File anyway without delay — evidence and witnesses decay even "
            "when the right does not.",
        ),
        related=("accident_compensation",),
        category="Accident",
    ),
    LimitationRule(
        id="domestic_violence",
        label="Application under the Domestic Violence Act",
        trigger="the date of the act of violence",
        days=None,
        act="Protection of Women from Domestic Violence Act, 2005",
        section="—",
        condonable=False,
        notes=(
            "No limitation period is prescribed. Where the conduct is continuing, "
            "the cause of action continues with it.",
        ),
        related=("domestic_violence",),
        category="Family",
    ),
    LimitationRule(
        id="maintenance_claim",
        label="Maintenance for wife, children or parents",
        trigger="the date maintenance was refused or neglected",
        days=None,
        act="Bharatiya Nagarik Suraksha Sanhita, 2023",
        section="Section 144",
        condonable=False,
        notes=(
            "No limitation on the right itself. Arrears, however, are ordinarily "
            "recoverable only for the twelve months before the application — so "
            "delay costs money even though it does not cost the right.",
        ),
        related=("maintenance",),
        category="Family",
    ),
]

BY_ID: dict[str, LimitationRule] = {r.id: r for r in RULES}


@dataclass
class LimitationResult:
    rule_id: str
    label: str
    trigger: str
    citation: str
    has_limitation: bool
    start_date: str
    deadline: str | None = None
    days_remaining: int | None = None
    expired: bool = False
    days_overdue: int | None = None
    #: none | urgent | soon | comfortable | expired
    urgency: str = "none"
    condonable: bool = False
    condonation_note: str = ""
    notes: list[str] = field(default_factory=list)
    related: list[str] = field(default_factory=list)
    #: Last day the court is actually open, after Section 4. Equals `deadline`
    #: unless it fell on a weekend or holiday.
    filing_date: str | None = None
    filing_date_confidence: str = "high"


def _add_period(start: date, rule: LimitationRule) -> date:
    """
    Add the limitation period to the start date.

    Calendar arithmetic, not 365-day arithmetic: three years from 29 February
    2024 is 28 February 2027, and one month from 31 January is 28 February.
    """
    year, month, day = start.year, start.month, start.day

    if rule.years:
        year += rule.years
    if rule.months:
        total = month - 1 + rule.months
        year += total // 12
        month = total % 12 + 1

    if rule.years or rule.months:
        # Clamp to the last valid day of the target month.
        while True:
            try:
                shifted = date(year, month, day)
                break
            except ValueError:
                day -= 1
        if rule.days:
            shifted += timedelta(days=rule.days)
        return shifted

    return start + timedelta(days=rule.days or 0)


def calculate(rule_id: str, event_date: date, today: date | None = None) -> LimitationResult:
    """Work out how long is left to act, or how long ago the right lapsed."""
    rule = BY_ID.get(rule_id)
    if rule is None:
        raise KeyError(f"Unknown limitation rule: {rule_id}")

    today = today or date.today()
    citation = f"{rule.act} — {rule.section}" if rule.section != "—" else rule.act

    if rule.days is None and rule.months is None and rule.years is None:
        return LimitationResult(
            rule_id=rule.id,
            label=rule.label,
            trigger=rule.trigger,
            citation=citation,
            has_limitation=False,
            start_date=event_date.isoformat(),
            urgency="none",
            notes=list(rule.notes),
            related=list(rule.related),
        )

    deadline = _add_period(event_date, rule)
    remaining = (deadline - today).days
    expired = remaining < 0

    if expired:
        urgency = "expired"
    elif remaining <= 7:
        urgency = "urgent"
    elif remaining <= 30:
        urgency = "soon"
    else:
        urgency = "comfortable"

    notes = list(rule.notes)
    notes.append(
        "The day the period runs from is excluded, per Section 12(1) of the "
        "Limitation Act, 1963."
    )

    # Section 4: if the last day is not a working day, the filing date moves
    # forward. Resolved exactly rather than left as a caveat.
    filing = holidays.resolve_filing_date(deadline)
    if filing["moved"]:
        notes.append(
            f"{deadline.isoformat()} is not a working day "
            f"({'; '.join(filing['reasons'])}), so the last day to file is "
            f"{filing['filing_date']}. {filing['note']}"
        )

    return LimitationResult(
        rule_id=rule.id,
        label=rule.label,
        trigger=rule.trigger,
        citation=citation,
        has_limitation=True,
        start_date=event_date.isoformat(),
        deadline=deadline.isoformat(),
        days_remaining=max(remaining, 0) if not expired else 0,
        expired=expired,
        days_overdue=abs(remaining) if expired else None,
        urgency=urgency,
        filing_date=filing["filing_date"],
        filing_date_confidence=filing["confidence"],
        condonable=rule.condonable,
        condonation_note=rule.condonation_note,
        notes=notes,
        related=list(rule.related),
    )


def catalogue() -> list[dict]:
    """Every rule, grouped for a picker."""
    return [
        {
            "id": r.id,
            "label": r.label,
            "category": r.category,
            "trigger": r.trigger,
            "citation": f"{r.act} — {r.section}" if r.section != "—" else r.act,
            "has_limitation": not (r.days is None and r.months is None and r.years is None),
        }
        for r in RULES
    ]
