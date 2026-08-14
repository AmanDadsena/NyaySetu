"""
Case timeline builder.

A litigator keeps a diary: file on the 3rd, written statement due in 30 days,
evidence after issues are framed, appeal within 90 of the decree. Working those
dates out by hand for every matter is the definition of tedious — it is
arithmetic, it is the same arithmetic each time, and getting one wrong costs a
client their case.

Given a matter type and the date it started, this produces every downstream
stage at once, marked by whether the period is a hard statutory bar or a
directory target the courts routinely exceed. That distinction is the whole
point: a lawyer needs to know which dates are real.

Where a stage depends on an event that has not happened yet — evidence follows
the framing of issues, which follows the written statement — the stage is
returned as pending with its trigger named, rather than being given a
fabricated date.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta


@dataclass(frozen=True)
class Stage:
    key: str
    label: str
    #: Days from the anchor event. None where the stage waits on something else.
    days: int | None
    #: What the period runs from. "filing" means the date supplied by the user;
    #: anything else names an event the user must date themselves.
    anchor: str = "filing"
    #: statutory — a bar the court cannot ignore.
    #: directory — a target; exceeding it does not invalidate anything.
    #: practical — no rule, just what actually happens.
    nature: str = "statutory"
    authority: str = ""
    note: str = ""


@dataclass(frozen=True)
class MatterType:
    id: str
    label: str
    category: str
    start_label: str
    stages: tuple[Stage, ...]
    related: tuple[str, ...] = ()


MATTERS: list[MatterType] = [
    MatterType(
        id="civil_suit",
        label="Civil suit (recovery, declaration, injunction)",
        category="Civil",
        start_label="Date the plaint was filed",
        stages=(
            Stage("summons", "Summons issued to defendant", 30, nature="practical",
                  authority="Order V, Code of Civil Procedure, 1908",
                  note="Depends on the court's roster; 30 days is typical, not prescribed."),
            Stage("written_statement", "Written statement due", 30,
                  anchor="service", nature="statutory",
                  authority="Order VIII Rule 1, CPC",
                  note="Extendable to 90 days for recorded reasons. In commercial suits "
                       "under the Commercial Courts Act, 120 days is an absolute outer "
                       "limit and the right to file is forfeited after it."),
            Stage("replication", "Replication, if any", 30, anchor="written_statement",
                  nature="practical"),
            Stage("issues", "Framing of issues", None, anchor="pleadings_complete",
                  nature="directory", authority="Order XIV, CPC",
                  note="Follows completion of pleadings. Date it once the written "
                       "statement is on record."),
            Stage("evidence_plaintiff", "Plaintiff's evidence", None, anchor="issues",
                  nature="practical"),
            Stage("evidence_defendant", "Defendant's evidence", None, anchor="evidence_plaintiff",
                  nature="practical"),
            Stage("arguments", "Final arguments", None, anchor="evidence_complete",
                  nature="practical"),
            Stage("judgment", "Judgment", 30, anchor="arguments", nature="directory",
                  authority="Order XX Rule 1, CPC",
                  note="Within 30 days of the conclusion of hearing, extendable to 60 "
                       "for exceptional reasons. Routinely exceeded."),
            Stage("appeal", "Appeal, if any", 90, anchor="decree", nature="statutory",
                  authority="Limitation Act, 1963, Article 116",
                  note="90 days to a High Court, 30 to a District Court. Time taken to "
                       "obtain a certified copy is excluded under Section 12(2)."),
            Stage("execution", "Execution of the decree", 4380, anchor="decree",
                  nature="statutory", authority="Limitation Act, 1963, Article 136",
                  note="12 years. Winning is not collecting."),
        ),
        related=("limitation_periods", "contract_essentials"),
    ),
    MatterType(
        id="consumer_case",
        label="Consumer complaint",
        category="Consumer",
        start_label="Date the complaint was filed",
        stages=(
            Stage("admission", "Admission and notice to the opposite party", 21,
                  nature="directory", authority="Consumer Protection Act, 2019, Section 36",
                  note="The Commission must decide admissibility within 21 days."),
            Stage("reply", "Opposite party's version due", 30, anchor="notice",
                  nature="statutory", authority="Consumer Protection Act, 2019, Section 38(2)(a)",
                  note="Extendable by 15 days, and no further. The Supreme Court held "
                       "this outer limit mandatory in New India Assurance v. Hilli "
                       "Multipurpose Cold Storage (2020)."),
            Stage("evidence", "Evidence by affidavit", None, anchor="reply",
                  nature="practical"),
            Stage("decision_simple", "Decision — no laboratory testing required", 90,
                  nature="directory", authority="Consumer Protection Act, 2019, Section 38(7)",
                  note="Three months from notice. Directory in practice."),
            Stage("decision_testing", "Decision — where goods require testing", 150,
                  nature="directory", authority="Consumer Protection Act, 2019, Section 38(7)"),
            Stage("appeal", "Appeal to the State Commission", 45, anchor="order",
                  nature="statutory", authority="Consumer Protection Act, 2019, Section 41",
                  note="An appellant ordered to pay must first deposit 50% of the amount."),
        ),
        related=("consumer_where_to_file", "consumer_how_to_file"),
    ),
    MatterType(
        id="cheque_case",
        label="Cheque bounce prosecution",
        category="Money recovery",
        start_label="Date of the bank's return memo",
        stages=(
            Stage("notice", "Statutory demand notice must be sent", 30, nature="statutory",
                  authority="Negotiable Instruments Act, 1881, Section 138(b)",
                  note="Cannot be extended. Miss it and no offence is made out."),
            Stage("payment_window", "Drawer's window to pay expires", 15, anchor="notice_served",
                  nature="statutory", authority="Negotiable Instruments Act, 1881, Section 138(c)",
                  note="Runs from when the drawer received the notice, not when you sent it."),
            Stage("complaint", "Complaint must be filed", 30, anchor="payment_window",
                  nature="statutory", authority="Negotiable Instruments Act, 1881, Section 142(b)",
                  note="Condonable on sufficient cause, unlike the notice period."),
            Stage("summons", "Summons to the accused", None, anchor="cognizance",
                  nature="practical"),
            Stage("interim_compensation", "Interim compensation may be sought", None,
                  anchor="plea", nature="practical",
                  authority="Negotiable Instruments Act, 1881, Section 143A",
                  note="Up to 20% of the cheque amount, payable within 60 days of the order."),
            Stage("trial", "Summary trial", 180, anchor="cognizance", nature="directory",
                  authority="Negotiable Instruments Act, 1881, Section 143(3)",
                  note="Six months. Widely exceeded."),
        ),
        related=("cheque_bounce",),
    ),
    MatterType(
        id="rti_track",
        label="RTI application through both appeals",
        category="Transparency",
        start_label="Date the RTI application was filed",
        stages=(
            Stage("reply", "Reply due from the Public Information Officer", 30,
                  nature="statutory", authority="Right to Information Act, 2005, Section 7(1)",
                  note="48 hours where the information concerns life or liberty. "
                       "No reply by day 30 is a deemed refusal under Section 7(2), and "
                       "the information must then be supplied free of charge."),
            Stage("first_appeal", "First appeal must be filed", 30, anchor="reply",
                  nature="statutory", authority="Right to Information Act, 2005, Section 19(1)",
                  note="Runs from the reply, or from the date it was due. No fee."),
            Stage("first_appeal_decision", "First appellate order due", 30,
                  anchor="first_appeal", nature="statutory",
                  authority="Right to Information Act, 2005, Section 19(6)",
                  note="Extendable to 45 days for recorded reasons."),
            Stage("second_appeal", "Second appeal to the Information Commission", 90,
                  anchor="first_appeal_decision", nature="statutory",
                  authority="Right to Information Act, 2005, Section 19(3)"),
        ),
        related=("rti_how_to_file", "rti_appeals"),
    ),
    MatterType(
        id="criminal_trial",
        label="Criminal case (accused or complainant)",
        category="Criminal",
        start_label="Date of arrest, or of the FIR",
        stages=(
            Stage("magistrate", "Production before a Magistrate", 1, nature="statutory",
                  authority="Constitution, Article 22(2); BNSS, 2023, Section 58",
                  note="Within 24 hours, excluding travel time. Detention beyond that "
                       "without authorisation is illegal."),
            Stage("default_bail_60", "Default bail arises — offences under 10 years", 60,
                  nature="statutory", authority="BNSS, 2023, Section 187",
                  note="If no charge sheet is filed by this date, the right to bail "
                       "accrues. It must be claimed while it subsists — it is lost the "
                       "moment the charge sheet is filed."),
            Stage("default_bail_90", "Default bail arises — offences of 10 years or more", 90,
                  nature="statutory", authority="BNSS, 2023, Section 187"),
            Stage("charges", "Framing of charges", 60, anchor="first_hearing",
                  nature="directory", authority="BNSS, 2023, Section 251",
                  note="New timeline introduced by the 2023 code."),
            Stage("judgment", "Judgment", 45, anchor="trial_conclusion", nature="directory",
                  authority="BNSS, 2023, Section 392",
                  note="Within 45 days of the conclusion of trial, extendable to 60."),
            Stage("appeal", "Appeal against conviction", 60, anchor="judgment",
                  nature="statutory", authority="Limitation Act, 1963, Articles 114–115",
                  note="30 days to a Sessions Court, 60 to a High Court."),
        ),
        related=("arrest_rights", "bail_default", "anticipatory_bail"),
    ),
    MatterType(
        id="posh_inquiry",
        label="Sexual harassment inquiry at work",
        category="Work",
        start_label="Date the complaint was made to the Committee",
        stages=(
            Stage("respondent_reply", "Respondent's reply due", 10, nature="statutory",
                  authority="POSH Rules, 2013, Rule 7(2)"),
            Stage("inquiry", "Inquiry must be completed", 90, nature="statutory",
                  authority="Sexual Harassment of Women at Workplace Act, 2013, Section 11(4)"),
            Stage("report", "Report to the employer", 10, anchor="inquiry",
                  nature="statutory", authority="POSH Act, 2013, Section 13(1)"),
            Stage("action", "Employer must act on the report", 60, anchor="report",
                  nature="statutory", authority="POSH Act, 2013, Section 13(4)"),
            Stage("appeal", "Appeal against the findings", 90, anchor="action",
                  nature="statutory", authority="POSH Act, 2013, Section 18"),
        ),
        related=("vishaka_posh",),
    ),
    MatterType(
        id="mutual_divorce",
        label="Divorce by mutual consent",
        category="Family",
        start_label="Date the joint petition was filed (first motion)",
        stages=(
            Stage("cooling_off", "Cooling-off period ends — second motion may be moved", 180,
                  nature="directory", authority="Hindu Marriage Act, 1955, Section 13B(2)",
                  note="Held directory, not mandatory, in Amardeep Singh v. Harveen Kaur "
                       "(2017). Waivable where the parties have already lived apart longer "
                       "than the statutory period and all issues are settled."),
            Stage("second_motion", "Outer limit for the second motion", 540,
                  nature="statutory", authority="Hindu Marriage Act, 1955, Section 13B(2)",
                  note="18 months from the first motion. Miss it and the petition lapses."),
        ),
        related=("divorce_mutual_consent",),
    ),
]

BY_ID: dict[str, MatterType] = {m.id: m for m in MATTERS}


@dataclass
class TimelineEntry:
    key: str
    label: str
    nature: str
    authority: str
    note: str
    anchor: str
    date: str | None = None
    days_from_start: int | None = None
    days_away: int | None = None
    status: str = "pending"  # scheduled | pending | passed
    #: Set when the stage waits on an event the user has not dated.
    awaiting: str | None = None


@dataclass
class Timeline:
    matter_id: str
    label: str
    start_label: str
    start_date: str
    entries: list[TimelineEntry] = field(default_factory=list)
    related: list[str] = field(default_factory=list)


#: Human phrasing for the anchors that are not the start date.
_ANCHOR_LABELS = {
    "service": "the date summons was served on the defendant",
    "written_statement": "the date the written statement was filed",
    "pleadings_complete": "the date pleadings closed",
    "issues": "the date issues were framed",
    "evidence_plaintiff": "the date the plaintiff's evidence closed",
    "evidence_complete": "the date evidence closed",
    "arguments": "the date arguments concluded",
    "decree": "the date of the decree",
    "notice": "the date notice was issued to the opposite party",
    "reply": "the date of the reply",
    "order": "the date of the order",
    "notice_served": "the date the drawer received your notice",
    "payment_window": "the date the 15-day payment window expired",
    "cognizance": "the date the court took cognizance",
    "plea": "the date the accused entered a plea",
    "first_hearing": "the date of the first hearing",
    "trial_conclusion": "the date the trial concluded",
    "first_appeal": "the date the first appeal was filed",
    "first_appeal_decision": "the date of the first appellate order",
    "judgment": "the date of judgment",
    "inquiry": "the date the inquiry was completed",
    "report": "the date the report reached the employer",
    "action": "the date the employer acted",
}


def build(matter_id: str, start: date, known: dict[str, str] | None = None,
          today: date | None = None) -> Timeline:
    """
    Compute the timeline.

    `known` optionally supplies dates for downstream anchors — service of
    summons, framing of issues — so a matter already in progress produces real
    dates for later stages rather than a wall of "pending".
    """
    matter = BY_ID.get(matter_id)
    if matter is None:
        raise KeyError(f"Unknown matter type: {matter_id}")

    today = today or date.today()
    anchors: dict[str, date] = {"filing": start}

    for key, value in (known or {}).items():
        try:
            anchors[key] = date.fromisoformat(value)
        except (ValueError, TypeError):
            continue

    entries: list[TimelineEntry] = []
    for stage in matter.stages:
        anchor_date = anchors.get(stage.anchor)

        if stage.days is None or anchor_date is None:
            entries.append(
                TimelineEntry(
                    key=stage.key,
                    label=stage.label,
                    nature=stage.nature,
                    authority=stage.authority,
                    note=stage.note,
                    anchor=stage.anchor,
                    status="pending",
                    awaiting=_ANCHOR_LABELS.get(stage.anchor, stage.anchor),
                )
            )
            continue

        due = anchor_date + timedelta(days=stage.days)
        away = (due - today).days
        entries.append(
            TimelineEntry(
                key=stage.key,
                label=stage.label,
                nature=stage.nature,
                authority=stage.authority,
                note=stage.note,
                anchor=stage.anchor,
                date=due.isoformat(),
                days_from_start=(due - start).days,
                days_away=away,
                status="passed" if away < 0 else "scheduled",
            )
        )

    return Timeline(
        matter_id=matter.id,
        label=matter.label,
        start_label=matter.start_label,
        start_date=start.isoformat(),
        entries=entries,
        related=list(matter.related),
    )


def catalogue() -> list[dict]:
    return [
        {
            "id": m.id,
            "label": m.label,
            "category": m.category,
            "start_label": m.start_label,
            "stage_count": len(m.stages),
            #: Anchors the caller can optionally supply to resolve later stages.
            "optional_anchors": [
                {"key": a, "label": _ANCHOR_LABELS.get(a, a)}
                for a in dict.fromkeys(
                    s.anchor for s in m.stages if s.anchor != "filing"
                )
            ],
        }
        for m in MATTERS
    ]
