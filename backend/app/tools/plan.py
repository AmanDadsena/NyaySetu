"""
One problem in, one plan out.

The toolkit grew as nine calculators, and each of them answers a question the
user did not ask. Nobody wakes up wanting to know a limitation period; they want
to know what to do about their landlord. Answering that takes the forum, the
deadline, the cost, the paperwork and the order to do it in — five lookups the
user currently has to know exist, find, and stitch together themselves.

This module does the stitching. It composes the existing tools rather than
re-implementing them, so a fix to the limitation table or the fee slabs shows up
here for free and the plan can never disagree with the calculator it came from.

The mapping tables below are deliberately thin. `forum.py` already knows which
limitation rules and which corpus passages belong to a problem, so only the
three links it does not carry — the fee matter, the document to send, and the
timeline to expect — are declared here.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from app.tools import documents, fees, forum, limitation, timeline


@dataclass(frozen=True)
class Situation:
    """A problem in the user's words, and the tools that answer it."""

    id: str
    #: How a person would describe this, not how a statute would.
    label: str
    #: The opening line of the plan: what this situation actually is.
    summary: str
    #: Rule id in `forum.py`. Everything else hangs off what that resolves to.
    forum_rule: str
    #: Matter id in `fees.py`, where a fee is payable at all.
    fee_matter: str | None = None
    #: Template id in `documents.py` — the letter that usually comes first.
    template: str | None = None
    #: Matter id in `timeline.py`, where the matter has a recognised shape.
    timeline_matter: str | None = None
    #: What to do, in order. The plan pairs these with the computed dates.
    steps: tuple[str, ...] = ()
    #: Shown next to the date field, so the user knows which date to enter.
    date_question: str = "When did the problem happen?"
    #: Shown next to the value field when the fee or forum depends on it.
    value_question: str | None = None


SITUATIONS: list[Situation] = [
    Situation(
        id="deposit_withheld",
        label="My landlord will not return my security deposit",
        summary=(
            "The deposit is your money held as security, not the landlord's income. "
            "It must come back when you hand over possession, less only what the "
            "agreement lets them deduct."
        ),
        forum_rule="landlord_tenant",
        fee_matter="civil_suit",
        template="legal_notice",
        timeline_matter="civil_suit",
        date_question="When did you hand back possession?",
        value_question="How much deposit is being withheld?",
        steps=(
            "Write to the landlord asking for the deposit and an itemised account of "
            "any deduction. Send it by registered post and keep the receipt.",
            "Gather your evidence: the agreement, proof the deposit was paid, "
            "photographs from when you moved in and when you left, final meter readings.",
            "If there is no reply, send the formal legal notice below with a deadline.",
            "Still nothing — file before the Rent Authority where your State has one, "
            "otherwise a recovery suit in the Court of Small Causes.",
        ),
    ),
    Situation(
        id="cheque_bounced",
        label="A cheque given to me bounced",
        summary=(
            "A dishonoured cheque is both a debt you can sue for and an offence under "
            "Section 138. The offence route has two hard deadlines and missing either "
            "one ends it, so the dates matter more than anything else here."
        ),
        forum_rule="cheque_bounce",
        fee_matter="cheque",
        template="cheque_notice",
        timeline_matter="cheque_case",
        date_question="What date is on the bank's dishonour memo?",
        value_question="What is the cheque for?",
        steps=(
            "Keep the returned cheque and the bank's dishonour memo. Everything runs "
            "from the date on that memo.",
            "Send the demand notice below within 30 days of the memo, by registered "
            "post. This is the step that cannot be recovered if missed.",
            "The drawer then has 15 days to pay. Do nothing until that window closes.",
            "If unpaid, file the complaint within 30 days of the window closing, "
            "before the Magistrate where the cheque was presented.",
        ),
    ),
    Situation(
        id="defective_purchase",
        label="I bought something defective, or paid for a service that failed",
        summary=(
            "Consumer law gives you a forum that is cheap, does not need a lawyer, and "
            "is chosen by what you paid — not by where the seller is."
        ),
        forum_rule="consumer",
        fee_matter="consumer",
        template="consumer_notice",
        timeline_matter="consumer_case",
        date_question="When did the defect appear, or the service fail?",
        value_question="What did you pay for the goods or service?",
        steps=(
            "Collect the invoice, the warranty, proof of payment, and photographs of "
            "the defect.",
            "Send the seller a written complaint and keep their reply, or proof that "
            "they did not answer. Commissions expect to see this first.",
            "Send the notice below giving them a final chance to put it right.",
            "File the complaint at the Commission decided by the amount you paid. "
            "You can file online through the e-Daakhil portal.",
        ),
    ),
    Situation(
        id="salary_unpaid",
        label="My employer has not paid my salary or dues",
        summary=(
            "Unpaid wages have a faster route than a civil suit. The authority under "
            "the wage legislation can order payment with compensation on top, and "
            "there is no court fee to reach it."
        ),
        forum_rule="unpaid_salary",
        fee_matter="tribunal",
        template="legal_notice",
        timeline_matter="civil_suit",
        date_question="When did the wages fall due?",
        value_question="How much is owed?",
        steps=(
            "Gather the appointment letter, payslips, bank statements showing earlier "
            "salary credits, and any written promise to pay.",
            "Ask in writing and keep the reply. An email is fine and is easier to prove.",
            "Send the notice below setting a deadline.",
            "File before the authority under the Payment of Wages Act or the Code on "
            "Wages. Provident fund and gratuity have their own separate routes.",
        ),
    ),
    Situation(
        id="rti_ignored",
        label="A public authority ignored or refused my RTI",
        summary=(
            "Silence is a deemed refusal, so you are not stuck waiting. Both appeals "
            "are free, need no lawyer, and the officer can be fined for the delay."
        ),
        forum_rule="rti_refused",
        fee_matter="rti",
        template="rti_first_appeal",
        timeline_matter="rti_track",
        date_question="When did you get the reply, or when did the 30 days expire?",
        steps=(
            "Keep the original application, the postal receipt, and any reply.",
            "File the first appeal below with the First Appellate Authority in the "
            "same public authority, within 30 days.",
            "If that fails or is ignored, go to the Information Commission — 90 days "
            "from the first appellate order.",
            "Ask the Commission for a penalty under Section 20 where the delay was "
            "without reasonable cause.",
        ),
    ),
    Situation(
        id="fir_refused",
        label="The police will not register my FIR",
        summary=(
            "Refusing to register a cognizable offence is not a discretion the police "
            "have. There is a defined ladder above the station, and the Magistrate sits "
            "at the top of it."
        ),
        forum_rule="police_inaction",
        template="fir_escalation",
        timeline_matter="criminal_trial",
        date_question="When did you try to report it?",
        steps=(
            "Write the complaint out and send it to the Superintendent of Police by "
            "registered post. The postal receipt is your proof you tried.",
            "If the SP does not act, apply to the Judicial Magistrate under Section "
            "175(3) BNSS, which can direct an investigation.",
            "Where the offence is against a woman or a child, the station cannot "
            "refuse on jurisdiction — a Zero FIR must be registered and transferred.",
            "Keep every acknowledgement. The refusal itself becomes part of the case.",
        ),
    ),
    Situation(
        id="road_accident",
        label="I was injured in a road accident",
        summary=(
            "Motor accident compensation does not depend on proving fault, and there "
            "is no limitation period. Do not let anyone tell you it is too late."
        ),
        forum_rule="road_accident",
        fee_matter="mact",
        template="legal_notice",
        date_question="When did the accident happen?",
        value_question="What compensation are you claiming, if you have a figure?",
        steps=(
            "Get the FIR, the accident report, and the vehicle and insurance details.",
            "Keep every medical bill, prescription and discharge summary — treatment "
            "cost is the part most often under-claimed.",
            "Get a disability certificate where there is lasting injury.",
            "File before the Motor Accidents Claims Tribunal for the district where "
            "the accident happened, where you live, or where the vehicle owner is.",
        ),
    ),
    Situation(
        id="domestic_violence",
        label="I am facing violence or abuse at home",
        summary=(
            "The Domestic Violence Act is civil, not criminal: it is built to get you "
            "protection, a place to live and money quickly, without you having to "
            "prosecute anyone first."
        ),
        forum_rule="domestic_violence",
        fee_matter="family",
        timeline_matter=None,
        date_question="When did the most recent incident happen?",
        steps=(
            "You can call 181 for the women's helpline or 112 in an emergency. A One "
            "Stop Centre gives police help, medical aid, legal aid and shelter in one "
            "place.",
            "Approach the Protection Officer for your district. They file the Domestic "
            "Incident Report for you — you do not need a lawyer and you do not have to "
            "go to the police first.",
            "The Magistrate can order protection, that you stay in the shared "
            "household, maintenance and custody. The target is 60 days.",
            "Free legal aid is yours by right as a woman, whatever your income.",
        ),
    ),
    Situation(
        id="maintenance_needed",
        label="I need maintenance from a spouse, child or parent",
        summary=(
            "Maintenance does not depend on your religion and does not require you to "
            "have filed for divorce. Interim maintenance can be ordered while the case "
            "is still running."
        ),
        forum_rule="maintenance",
        fee_matter="family",
        date_question="When did the support stop?",
        value_question="What is the other party's monthly income, if you know it?",
        steps=(
            "Collect what you can showing their income: payslips, tax returns, bank "
            "statements, property papers, business records.",
            "Record your own expenses — rent, school fees, medical costs.",
            "Apply under Section 144 BNSS, or under your personal law, or under the "
            "Domestic Violence Act. They can run together.",
            "Ask for interim maintenance at the first hearing rather than waiting for "
            "the case to end.",
        ),
    ),
    Situation(
        id="workplace_harassment",
        label="I was sexually harassed at work",
        summary=(
            "Every workplace with ten or more employees must have an Internal "
            "Committee, and the complaint goes there — not to your manager, and not to "
            "HR as a favour."
        ),
        forum_rule="workplace_harassment",
        fee_matter="tribunal",
        timeline_matter="posh_inquiry",
        date_question="When did the incident happen?",
        steps=(
            "Write down what happened with dates, and keep any messages, emails or "
            "witness names.",
            "Complain in writing to the Internal Committee within three months. That "
            "period can be extended for good reason.",
            "Ask for interim relief — a transfer, leave, or that the respondent be kept "
            "away from you while the inquiry runs.",
            "Where there is no Internal Committee, go to the Local Committee at the "
            "District Officer.",
        ),
    ),
    Situation(
        id="online_fraud",
        label="I was defrauded online, or money left my account",
        summary=(
            "Speed decides how much you get back. Reporting within three working days "
            "generally means you owe nothing, and a report within the first hour can "
            "get the transfer frozen before it moves on."
        ),
        forum_rule="cyber_fraud",
        fee_matter="consumer",
        template="legal_notice",
        date_question="When did the transaction happen?",
        value_question="How much was taken?",
        steps=(
            "Call 1930 or report at cybercrime.gov.in immediately. This is the step "
            "that actually recovers money.",
            "Tell the bank on its 24x7 number and insist on a written acknowledgement "
            "with a ticket number.",
            "Keep screenshots of the transaction, any messages, and the numbers used.",
            "If the bank does not resolve it in 90 days, escalate to the RBI "
            "Ombudsman at cms.rbi.org.in.",
        ),
    ),
    Situation(
        id="insurance_rejected",
        label="My insurance claim was rejected or delayed",
        summary=(
            "An insurer must give reasons in writing. Rejection is a decision you can "
            "appeal, free, without a lawyer, and without going to court."
        ),
        forum_rule="insurance_rejected",
        fee_matter="consumer",
        template="consumer_notice",
        timeline_matter="consumer_case",
        date_question="When was the claim rejected, or when should it have been paid?",
        value_question="What is the claim worth?",
        steps=(
            "Get the rejection in writing with reasons, and a copy of the full policy "
            "including the schedule.",
            "Complain to the insurer's grievance cell and give them 30 days.",
            "Go to the Insurance Ombudsman — free, no lawyer, up to fifty lakh rupees, "
            "within a year of the insurer's final reply.",
            "A consumer commission remains open, and an Ombudsman award you reject "
            "does not close it.",
        ),
    ),
    Situation(
        id="senior_neglect",
        label="My children will not look after me",
        summary=(
            "The Maintenance and Welfare of Parents and Senior Citizens Act is "
            "deliberately quick and lawyer-free, and it can undo a property transfer "
            "made on a promise of care that was then broken."
        ),
        forum_rule="senior_citizen",
        fee_matter="family",
        date_question="When did they stop supporting you?",
        steps=(
            "Apply to the Maintenance Tribunal for your sub-division. A lawyer is not "
            "permitted, so nobody can out-lawyer you.",
            "Bring proof of relationship and of their means.",
            "If you transferred property on a promise they would look after you, ask "
            "the Tribunal to declare that transfer void.",
            "The Tribunal should decide within 90 days.",
        ),
    ),
]

BY_ID: dict[str, Situation] = {s.id: s for s in SITUATIONS}


@dataclass
class Deadline:
    """One computed date in the plan, in the order it must be met."""

    rule_id: str
    label: str
    trigger: str
    citation: str
    #: False where the law sets no time limit at all — a motor accident claim,
    #: for instance. Distinct from "we could not compute one".
    has_limitation: bool
    deadline: str | None
    filing_date: str | None
    days_remaining: int | None
    expired: bool
    urgency: str
    condonable: bool
    condonation_note: str
    notes: list[str] = field(default_factory=list)


@dataclass
class CasePlan:
    situation_id: str
    label: str
    summary: str
    event_date: str
    forum: dict
    value_tier: str | None
    deadlines: list[Deadline]
    steps: list[str]
    documents_to_gather: list[str]
    fee: dict | None
    template: dict | None
    stages: list[dict]
    #: Corpus passage ids behind this plan, for the "read the law" links.
    law: list[str]
    #: The single most urgent thing, precomputed so the UI does not have to
    #: re-derive it and risk disagreeing with the list above.
    headline: str


def catalogue() -> list[dict]:
    """The situations a plan can be built for, for the picker."""
    return [
        {
            "id": s.id,
            "label": s.label,
            "summary": s.summary,
            "date_question": s.date_question,
            "value_question": s.value_question,
            "needs_value": s.value_question is not None,
        }
        for s in SITUATIONS
    ]


def _headline(deadlines: list[Deadline], label: str) -> str:
    """
    The one sentence worth reading if the user reads nothing else.

    Expired deadlines outrank urgent ones, and an urgent deadline outranks the
    generic description — someone with eleven days left should not have to
    notice that for themselves.
    """
    expired = [d for d in deadlines if d.expired]
    if expired:
        first = expired[0]
        if first.condonable:
            return (
                f"The deadline has passed — {first.label}. It can still be condoned, "
                f"but you must explain the delay when you file."
            )
        return f"The deadline has passed — {first.label}."

    live = [d for d in deadlines if d.days_remaining is not None]
    if live:
        soonest = min(live, key=lambda d: d.days_remaining or 0)
        days = soonest.days_remaining or 0
        urgency = " Act now." if days <= 30 else ""
        return f"{days} days left — {soonest.label}.{urgency}"

    # A rule that exists but sets no period is worth saying out loud. People
    # routinely assume they are too late and never file.
    timeless = [d for d in deadlines if not d.has_limitation]
    if timeless:
        return (
            f"No time limit applies to {timeless[0].label.lower()} — being late is "
            f"not a reason you cannot file."
        )

    return f"No limitation period governs this. {label}."


def build(
    situation_id: str,
    event_date: date,
    claim_value: float | None = None,
    state: str | None = None,
    today: date | None = None,
) -> CasePlan:
    """Assemble every tool's answer for one situation into a single plan."""
    situation = BY_ID.get(situation_id)
    if situation is None:
        raise KeyError(f"Unknown situation: {situation_id}")

    routed = forum.route(situation.forum_rule, claim_value)

    # Deadlines come from the forum rule's own list, so the plan cannot drift
    # out of step with the "where do I file" answer.
    deadlines: list[Deadline] = []
    for rule in routed.limitation:
        result = limitation.calculate(rule["id"], event_date, today=today)
        deadlines.append(
            Deadline(
                rule_id=result.rule_id,
                label=result.label,
                trigger=result.trigger,
                citation=result.citation,
                has_limitation=result.has_limitation,
                deadline=result.deadline,
                filing_date=result.filing_date,
                days_remaining=result.days_remaining,
                expired=result.expired,
                urgency=result.urgency,
                condonable=result.condonable,
                condonation_note=result.condonation_note,
                notes=list(result.notes),
            )
        )
    # Soonest first; a plan is only useful in the order things must be done.
    deadlines.sort(key=lambda d: (d.deadline is None, d.deadline or ""))

    fee: dict | None = None
    if situation.fee_matter:
        try:
            fee = fees.calculate(situation.fee_matter, claim_value or 0.0, state).__dict__
        except KeyError:
            fee = None

    template: dict | None = None
    if situation.template:
        for entry in documents.catalogue():
            if entry["id"] == situation.template:
                template = entry
                break

    stages: list[dict] = []
    if situation.timeline_matter:
        try:
            built = timeline.build(situation.timeline_matter, event_date)
            stages = [e.__dict__ for e in built.entries]
        except KeyError:
            stages = []

    return CasePlan(
        situation_id=situation.id,
        label=situation.label,
        summary=situation.summary,
        event_date=event_date.isoformat(),
        forum=routed.forum,
        value_tier=routed.value_tier,
        deadlines=deadlines,
        steps=list(situation.steps),
        documents_to_gather=list(routed.forum.get("documents", [])),
        fee=fee,
        template=template,
        stages=stages,
        law=list(routed.related),
        headline=_headline(deadlines, situation.label),
    )
