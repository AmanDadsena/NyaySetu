"""
Legal document generator.

An RTI application is a page of text with five variables in it. A cheque-bounce
demand notice is a form with a statutory deadline attached. People pay ₹500 to
₹2,000 to have these filled in, and the reason is not that they are hard — it
is that getting one clause wrong makes the document useless, and nobody wants
to find that out later.

So these are templates, not generated text. A model would produce something
plausible that might omit the statutory language a notice needs to be valid.
Every template below is deterministic, cites the provision that makes it work,
and carries a checklist of what to do after printing it.

Nothing here is legal advice, and a generated document does not become correct
because software produced it. Each one ends with the same instruction: read it
before you sign it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


@dataclass(frozen=True)
class Field:
    name: str
    label: str
    #: text | textarea | date | number
    kind: str = "text"
    required: bool = True
    placeholder: str = ""
    help: str = ""


@dataclass(frozen=True)
class Template:
    id: str
    title: str
    description: str
    category: str
    act: str
    section: str
    fields: tuple[Field, ...]
    #: Steps to follow once the document is printed and signed.
    after: tuple[str, ...]
    #: Limitation rule ids that constrain when this must be sent or filed.
    limitation: tuple[str, ...] = ()
    related: tuple[str, ...] = ()
    fee: str = ""


_APPLICANT = (
    Field("applicant_name", "Your full name"),
    Field("applicant_address", "Your full postal address", kind="textarea"),
    Field("applicant_phone", "Your phone number", required=False),
    Field("applicant_email", "Your email", required=False),
)


TEMPLATES: dict[str, Template] = {
    # ── RTI ─────────────────────────────────────────────────────────────
    "rti_application": Template(
        id="rti_application",
        title="RTI application",
        description=(
            "Ask any public authority for information. You do not have to give a "
            "reason for wanting it, and you cannot be asked for one."
        ),
        category="Transparency",
        act="Right to Information Act, 2005",
        section="Section 6(1)",
        fee="₹10, or nothing if you hold a BPL card.",
        fields=_APPLICANT + (
            Field("authority_name", "Public authority",
                  placeholder="e.g. Office of the Municipal Commissioner, Pune",
                  help="Address it to the Public Information Officer of that department."),
            Field("authority_address", "Authority's address", kind="textarea"),
            Field("subject", "Subject of your request",
                  placeholder="e.g. Status of road repair sanctioned for Ward 14"),
            Field("information_sought", "Information you want", kind="textarea",
                  help="Number your questions. Ask for specific records — a file, an order, "
                       "a date, an amount — rather than asking why something happened."),
            Field("period_from", "Period covered — from", kind="date", required=False),
            Field("period_to", "Period covered — to", kind="date", required=False),
            Field("is_bpl", "Do you hold a BPL card?", kind="text", required=False,
                  placeholder="yes / no", help="BPL cardholders pay no fee."),
        ),
        after=(
            "Attach the ₹10 fee — Indian Postal Order, demand draft, or court fee stamp, "
            "as your State permits. BPL cardholders attach a copy of the card instead.",
            "Send by registered post with acknowledgement due, and keep the receipt. "
            "The receipt is your proof of the date, which decides your appeal deadline.",
            "For Central Government departments you can file online at rtionline.gov.in.",
            "A reply is due within 30 days — 48 hours if it concerns someone's life or liberty.",
            "No reply within 30 days counts as a refusal. You can appeal from that date.",
        ),
        limitation=("rti_first_appeal",),
        related=("rti_how_to_file", "rti_exemptions"),
    ),
    "rti_first_appeal": Template(
        id="rti_first_appeal",
        title="RTI first appeal",
        description="Use when your RTI was refused, answered incompletely, or ignored.",
        category="Transparency",
        act="Right to Information Act, 2005",
        section="Section 19(1)",
        fee="None.",
        fields=_APPLICANT + (
            Field("authority_name", "Public authority"),
            Field("authority_address", "First Appellate Authority's address", kind="textarea"),
            Field("rti_date", "Date of your original RTI application", kind="date"),
            Field("rti_subject", "Subject of that application"),
            Field("reply_date", "Date of the reply, if you got one", kind="date", required=False,
                  help="Leave blank if the 30 days simply passed with no reply."),
            Field("grounds", "Why the reply was inadequate", kind="textarea",
                  help="Be specific: which question went unanswered, what was withheld "
                       "and under which exemption, or that nothing arrived at all."),
        ),
        after=(
            "File within 30 days of the reply, or of the date the reply was due.",
            "No fee is payable. Do not let anyone charge you one.",
            "Ask expressly for a penalty under Section 20 — ₹250 per day up to ₹25,000 — "
            "where the delay was without reasonable cause. Appeals that ask for it are "
            "taken more seriously.",
            "If this fails, a second appeal lies to the Information Commission within 90 days.",
        ),
        limitation=("rti_first_appeal", "rti_second_appeal"),
        related=("rti_appeals",),
    ),

    # ── Consumer ────────────────────────────────────────────────────────
    "consumer_notice": Template(
        id="consumer_notice",
        title="Notice to a seller before filing a consumer complaint",
        description=(
            "Send this before you file. It is not strictly compulsory, but it "
            "establishes your date, often produces a refund on its own, and a "
            "Commission will ask whether you gave them a chance to put it right."
        ),
        category="Consumer",
        act="Consumer Protection Act, 2019",
        section="Section 2(6)",
        fee="Cost of registered post only.",
        fields=_APPLICANT + (
            Field("opposite_name", "Seller or service provider's name"),
            Field("opposite_address", "Their address", kind="textarea"),
            Field("purchase_date", "Date of purchase or service", kind="date"),
            Field("amount", "Amount paid (₹)", kind="number"),
            Field("invoice_no", "Invoice or order number", required=False),
            Field("problem", "What went wrong", kind="textarea",
                  help="Facts and dates only. What you bought, what failed, when, and "
                       "what you have already tried."),
            Field("relief", "What you want", kind="textarea",
                  placeholder="e.g. Full refund of ₹32,000 and compensation for the inconvenience"),
            Field("deadline_days", "Days you are giving them to respond", kind="number",
                  required=False, placeholder="15"),
        ),
        after=(
            "Send by registered post with acknowledgement due and keep the receipt.",
            "Keep a signed copy for yourself.",
            "If they do not respond within the period you gave, file at edaakhil.nic.in.",
            "Your two-year limitation runs from when the problem arose, not from this notice.",
        ),
        limitation=("consumer_complaint",),
        related=("consumer_how_to_file", "consumer_where_to_file"),
    ),

    # ── Cheque bounce ───────────────────────────────────────────────────
    "cheque_notice": Template(
        id="cheque_notice",
        title="Cheque bounce demand notice",
        description=(
            "The statutory notice under Section 138. Without it, and without it "
            "being sent in time, there is no offence to prosecute — so this is the "
            "single most deadline-sensitive document here."
        ),
        category="Money recovery",
        act="Negotiable Instruments Act, 1881",
        section="Section 138(b)",
        fee="Cost of registered post only.",
        fields=_APPLICANT + (
            Field("drawer_name", "Name of the person who gave you the cheque"),
            Field("drawer_address", "Their address", kind="textarea"),
            Field("cheque_no", "Cheque number"),
            Field("cheque_date", "Date on the cheque", kind="date"),
            Field("cheque_amount", "Cheque amount (₹)", kind="number"),
            Field("drawer_bank", "Bank and branch the cheque is drawn on"),
            Field("deposit_date", "Date you deposited it", kind="date"),
            Field("return_date", "Date of the bank's return memo", kind="date",
                  help="Your 30 days run from this date. Get it right."),
            Field("return_reason", "Reason on the return memo",
                  placeholder="e.g. Funds insufficient"),
            Field("liability_reason", "What the cheque was for", kind="textarea",
                  help="A cheque is only actionable if it discharges a legally enforceable "
                       "debt. Say what the debt was — a loan, an invoice, an agreement."),
        ),
        after=(
            "Send within 30 days of the bank's return memo. This cannot be extended.",
            "Send by registered post with acknowledgement due to the address on record. "
            "Refusal to accept still counts as service.",
            "Keep the postal receipt, the tracking printout, and a signed copy.",
            "The drawer then has 15 days from receiving it to pay.",
            "If they do not, file your complaint within 30 days of that 15-day window "
            "closing — before the Magistrate where the bank branch is located.",
            "Do not part with the original cheque or the return memo. The court needs them.",
        ),
        limitation=("cheque_notice", "cheque_complaint"),
        related=("cheque_bounce",),
    ),

    # ── Police ──────────────────────────────────────────────────────────
    "fir_escalation": Template(
        id="fir_escalation",
        title="Complaint to the Superintendent of Police when an FIR is refused",
        description=(
            "The first formal step when a police station will not register your FIR. "
            "The SP must investigate, or direct an investigation, if the complaint "
            "discloses a cognizable offence."
        ),
        category="Police",
        act="Bharatiya Nagarik Suraksha Sanhita, 2023",
        section="Section 173(4)",
        fee="Cost of registered post only.",
        fields=_APPLICANT + (
            Field("sp_office", "Office of the Superintendent of Police",
                  placeholder="e.g. Superintendent of Police, Nagpur Rural"),
            Field("police_station", "Police station that refused"),
            Field("attempt_date", "Date you tried to register the FIR", kind="date"),
            Field("officer_name", "Name or number of the officer, if you noted it",
                  required=False),
            Field("incident_date", "Date of the incident", kind="date"),
            Field("incident", "What happened", kind="textarea",
                  help="Plain chronological facts. Where, when, who, and what was done."),
            Field("offence_reason", "Why this is a cognizable offence", kind="textarea",
                  required=False,
                  help="Optional. Name the offence if you know it — theft, assault, cheating."),
        ),
        after=(
            "Send by registered post with acknowledgement due. Keep the receipt — it "
            "proves the date you tried, which matters if you go to the Magistrate next.",
            "Send a copy to the police station itself.",
            "If the SP does not act, apply to the Judicial Magistrate under Section 175(3) "
            "of the BNSS, 2023, attaching this complaint and the postal receipt.",
            "A station cannot refuse because the offence happened elsewhere — that is what "
            "a Zero FIR is for.",
            "Free legal aid is available on 15100.",
        ),
        related=("fir_refusal_remedy", "zero_fir", "police_complaint_against"),
    ),

    # ── General ─────────────────────────────────────────────────────────
    "legal_notice": Template(
        id="legal_notice",
        title="General legal notice",
        description=(
            "A formal demand before litigation. Used for unpaid dues, breach of an "
            "agreement, or to demand that something stop."
        ),
        category="General",
        act="—",
        section="—",
        fee="Cost of registered post only.",
        fields=_APPLICANT + (
            Field("recipient_name", "Recipient's name"),
            Field("recipient_address", "Recipient's address", kind="textarea"),
            Field("subject", "Subject"),
            Field("facts", "The facts", kind="textarea",
                  help="Numbered, chronological, and verifiable. Dates and amounts. "
                       "Leave out adjectives — a notice is stronger without them."),
            Field("demand", "What you demand", kind="textarea"),
            Field("deadline_days", "Days you are giving them to comply", kind="number",
                  placeholder="15"),
        ),
        after=(
            "Send by registered post with acknowledgement due, and keep the receipt.",
            "Keep a signed copy. This becomes an annexure if you sue.",
            "A notice sent through an advocate carries more weight, but one you send "
            "yourself is equally valid in law.",
            "Check your limitation period before you rely on the notice period — sending "
            "a notice does not stop the clock.",
        ),
        limitation=("suit_money",),
        related=("contract_essentials", "limitation_periods"),
    ),
}


# ── Rendering ───────────────────────────────────────────────────────────
def _fmt_date(value: str) -> str:
    """Render an ISO date the way Indian correspondence does."""
    try:
        return date.fromisoformat(value).strftime("%d %B %Y")
    except (ValueError, TypeError):
        return value or "____________"


def _v(data: dict, key: str, blank: str = "____________") -> str:
    value = str(data.get(key, "") or "").strip()
    return value or blank


def _money(data: dict, key: str, blank: str = "____________") -> str:
    """
    Format an amount in the Indian grouping — 8,50,000, not 850,000.

    A notice quoting a figure in a foreign grouping reads as though it was
    produced by something that does not know where it is.
    """
    raw = str(data.get(key, "") or "").strip().replace(",", "")
    if not raw:
        return blank
    try:
        amount = float(raw)
    except ValueError:
        return raw

    whole = int(abs(amount))
    paise = abs(amount) - whole
    digits = str(whole)

    if len(digits) > 3:
        last3, rest = digits[-3:], digits[:-3]
        groups = []
        while len(rest) > 2:
            groups.insert(0, rest[-2:])
            rest = rest[:-2]
        if rest:
            groups.insert(0, rest)
        grouped = ",".join(groups + [last3])
    else:
        grouped = digits

    if paise > 0.004:
        grouped += f".{round(paise * 100):02d}"
    return ("-" if amount < 0 else "") + grouped


def _numbered(text: str) -> str:
    """Turn free text into numbered paragraphs, one per non-empty line."""
    lines = [ln.strip() for ln in str(text or "").splitlines() if ln.strip()]
    if not lines:
        return "   1. ____________"
    return "\n".join(f"   {i}. {line}" for i, line in enumerate(lines, 1))


def _sender_block(data: dict) -> str:
    parts = [_v(data, "applicant_name"), _v(data, "applicant_address")]
    if data.get("applicant_phone"):
        parts.append(f"Phone: {data['applicant_phone']}")
    if data.get("applicant_email"):
        parts.append(f"Email: {data['applicant_email']}")
    return "\n".join(parts)


def _footer(template: Template) -> str:
    return (
        "\n\n" + "─" * 66 + "\n"
        "Generated by Nyaysetu. This is a template, not legal advice.\n"
        "Read it in full and correct anything that does not match your facts\n"
        "before you sign and send it. Free legal aid: 15100.\n"
    )


def _render_rti_application(d: dict, t: Template) -> str:
    period = ""
    if d.get("period_from") or d.get("period_to"):
        period = (
            f"\nPeriod to which the information relates: "
            f"{_fmt_date(d.get('period_from', ''))} to {_fmt_date(d.get('period_to', ''))}\n"
        )
    fee_line = (
        "I hold a Below Poverty Line card, a copy of which is enclosed, and am "
        "therefore exempt from the fee under Section 7(5)."
        if str(d.get("is_bpl", "")).strip().lower() in {"yes", "y", "true"}
        else "The prescribed fee of ₹10 is enclosed."
    )

    return f"""To,
The Public Information Officer
{_v(d, 'authority_name')}
{_v(d, 'authority_address')}

From,
{_sender_block(d)}

Date: {date.today().strftime('%d %B %Y')}

Subject: Application under the Right to Information Act, 2005 — {_v(d, 'subject')}

Sir/Madam,

Under Section 6(1) of the Right to Information Act, 2005, I request the
following information:

{_numbered(d.get('information_sought', ''))}
{period}
{fee_line}

Please supply the information within 30 days as required by Section 7(1). If
any part of it is held to be exempt, please specify the exact provision relied
on and supply the remainder, as Section 10(1) requires.

If this application relates to another public authority in whole or in part,
please transfer it under Section 6(3) and inform me.

Yours faithfully,


{_v(d, 'applicant_name')}

Enclosure: Fee of ₹10 / copy of BPL card
"""


def _render_rti_first_appeal(d: dict, t: Template) -> str:
    if d.get("reply_date"):
        grievance = (
            f"A reply dated {_fmt_date(d['reply_date'])} was received. It is "
            f"inadequate for the reasons set out below."
        )
    else:
        grievance = (
            "No reply has been received within the 30 days prescribed by Section 7(1). "
            "Under Section 7(2) this is deemed a refusal."
        )

    return f"""To,
The First Appellate Authority
{_v(d, 'authority_name')}
{_v(d, 'authority_address')}

From,
{_sender_block(d)}

Date: {date.today().strftime('%d %B %Y')}

Subject: First appeal under Section 19(1) of the Right to Information Act, 2005

Sir/Madam,

I filed an application under the Right to Information Act, 2005 dated
{_fmt_date(d.get('rti_date', ''))} on the subject of "{_v(d, 'rti_subject')}".

{grievance}

Grounds of appeal:

{_numbered(d.get('grounds', ''))}

I therefore request that the Public Information Officer be directed to supply
the information sought, in full and free of cost, the delay having exceeded the
period prescribed by Section 7(1) — see Section 7(6).

I further request that action be considered under Section 20 of the Act, which
provides for a penalty of ₹250 per day, up to ₹25,000, where information is
refused or delayed without reasonable cause.

A copy of the original application and of the reply, if any, is enclosed.

Yours faithfully,


{_v(d, 'applicant_name')}

Enclosures: 1. Copy of the RTI application dated {_fmt_date(d.get('rti_date', ''))}
            2. Proof of fee paid
            3. Copy of the reply received, if any
"""


def _render_consumer_notice(d: dict, t: Template) -> str:
    days = _v(d, "deadline_days", "15")
    return f"""To,
{_v(d, 'opposite_name')}
{_v(d, 'opposite_address')}

From,
{_sender_block(d)}

Date: {date.today().strftime('%d %B %Y')}

Subject: Notice regarding deficiency in service / defect in goods, and demand
         for redress

Sir/Madam,

1. On {_fmt_date(d.get('purchase_date', ''))} I paid ₹{_money(d, 'amount', '____')} to you
   {'against invoice/order number ' + str(d['invoice_no']) if d.get('invoice_no') else ''}
   for goods or services supplied by you.

2. The following defect or deficiency has arisen:

{_numbered(d.get('problem', ''))}

3. I am a "consumer" within the meaning of Section 2(7) of the Consumer
   Protection Act, 2019, and the above amounts to a defect or deficiency within
   the meaning of Sections 2(10) and 2(11) of that Act.

4. I accordingly call upon you to:

{_numbered(d.get('relief', ''))}

5. Please comply within {days} days of receiving this notice. If you do not, I
   shall file a complaint before the appropriate Consumer Disputes Redressal
   Commission and claim, in addition, compensation for the deficiency, for the
   mental agony caused, and the costs of the proceedings.

This notice is sent without prejudice to any other remedy available to me.

Yours faithfully,


{_v(d, 'applicant_name')}
"""


def _render_cheque_notice(d: dict, t: Template) -> str:
    return f"""To,
{_v(d, 'drawer_name')}
{_v(d, 'drawer_address')}

From,
{_sender_block(d)}

Date: {date.today().strftime('%d %B %Y')}

BY REGISTERED POST WITH ACKNOWLEDGEMENT DUE

Subject: Notice under Section 138(b) of the Negotiable Instruments Act, 1881

Sir/Madam,

1. You are liable to pay me the sum of ₹{_money(d, 'cheque_amount', '____')} on account of
   the following legally enforceable debt or liability:

{_numbered(d.get('liability_reason', ''))}

2. Towards discharge of that liability, you issued cheque number
   {_v(d, 'cheque_no')} dated {_fmt_date(d.get('cheque_date', ''))} for
   ₹{_money(d, 'cheque_amount', '____')}, drawn on {_v(d, 'drawer_bank')}.

3. I presented the said cheque for encashment on
   {_fmt_date(d.get('deposit_date', ''))}. It was returned unpaid by the bank vide
   its memo dated {_fmt_date(d.get('return_date', ''))} with the endorsement
   "{_v(d, 'return_reason')}".

4. The dishonour of the said cheque constitutes an offence under Section 138 of
   the Negotiable Instruments Act, 1881.

5. I hereby call upon you to pay the said sum of ₹{_money(d, 'cheque_amount', '____')}
   within FIFTEEN (15) DAYS of receipt of this notice.

6. Should you fail to pay within the said period, I shall be constrained to
   initiate criminal proceedings against you under Section 138 of the
   Negotiable Instruments Act, 1881, which is punishable with imprisonment for
   a term which may extend to two years, or with fine which may extend to twice
   the amount of the cheque, or with both — besides civil proceedings for
   recovery, entirely at your risk as to costs and consequences.

Yours faithfully,


{_v(d, 'applicant_name')}

Enclosures: 1. Copy of the dishonoured cheque
            2. Copy of the bank return memo dated {_fmt_date(d.get('return_date', ''))}
"""


def _render_fir_escalation(d: dict, t: Template) -> str:
    officer = (
        f" The officer concerned was {d['officer_name']}."
        if d.get("officer_name") else ""
    )
    offence = ""
    if d.get("offence_reason"):
        offence = f"\n4. The facts disclose a cognizable offence, in that:\n\n{_numbered(d['offence_reason'])}\n"

    return f"""To,
{_v(d, 'sp_office')}

From,
{_sender_block(d)}

Date: {date.today().strftime('%d %B %Y')}

BY REGISTERED POST WITH ACKNOWLEDGEMENT DUE

Subject: Complaint under Section 173(4) of the Bharatiya Nagarik Suraksha
         Sanhita, 2023 — refusal to register a First Information Report by
         {_v(d, 'police_station')}

Sir/Madam,

1. On {_fmt_date(d.get('incident_date', ''))} the following occurred:

{_numbered(d.get('incident', ''))}

2. On {_fmt_date(d.get('attempt_date', ''))} I attended {_v(d, 'police_station')} and
   sought to have a First Information Report registered in respect of the above.
   The station declined to register it.{officer}

3. Section 173(1) of the Bharatiya Nagarik Suraksha Sanhita, 2023 requires that
   information relating to the commission of a cognizable offence be reduced to
   writing and registered, irrespective of the area in which the offence was
   committed.
{offence}
5. I therefore request, under Section 173(4) of the said Sanhita, that you
   either investigate the matter yourself or direct an investigation to be made
   by a subordinate officer, and that I be informed of the action taken.

6. I place on record that should no action be taken on this complaint, I shall
   move the jurisdictional Judicial Magistrate under Section 175(3) of the
   Sanhita.

A copy of this complaint has been sent to {_v(d, 'police_station')}.

Yours faithfully,


{_v(d, 'applicant_name')}
"""


def _render_legal_notice(d: dict, t: Template) -> str:
    days = _v(d, "deadline_days", "15")
    return f"""To,
{_v(d, 'recipient_name')}
{_v(d, 'recipient_address')}

From,
{_sender_block(d)}

Date: {date.today().strftime('%d %B %Y')}

BY REGISTERED POST WITH ACKNOWLEDGEMENT DUE

Subject: {_v(d, 'subject')}

Sir/Madam,

Under instructions from and on behalf of myself, I address you as follows:

{_numbered(d.get('facts', ''))}

In the premises, I hereby call upon you to:

{_numbered(d.get('demand', ''))}

You are called upon to comply within {days} days of receipt of this notice,
failing which I shall be constrained to initiate such civil and/or criminal
proceedings as are available to me, entirely at your risk as to costs and
consequences, and this notice shall be relied upon as evidence of the demand
having been made.

A copy of this notice is retained for record.

Yours faithfully,


{_v(d, 'applicant_name')}
"""


_RENDERERS = {
    "rti_application": _render_rti_application,
    "rti_first_appeal": _render_rti_first_appeal,
    "consumer_notice": _render_consumer_notice,
    "cheque_notice": _render_cheque_notice,
    "fir_escalation": _render_fir_escalation,
    "legal_notice": _render_legal_notice,
}


@dataclass
class GeneratedDocument:
    template_id: str
    title: str
    body: str
    citation: str
    after: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)
    limitation: list[str] = field(default_factory=list)
    related: list[str] = field(default_factory=list)


def generate(template_id: str, data: dict) -> GeneratedDocument:
    """
    Fill a template.

    Missing required fields are reported rather than refused: a half-filled
    document with visible blanks is more useful than an error, because people
    print it and fill the rest by hand.
    """
    template = TEMPLATES.get(template_id)
    if template is None:
        raise KeyError(f"Unknown template: {template_id}")

    missing = [
        f.label for f in template.fields
        if f.required and not str(data.get(f.name, "") or "").strip()
    ]

    body = _RENDERERS[template_id](data, template) + _footer(template)
    citation = (
        f"{template.act} — {template.section}"
        if template.section != "—" else "General civil practice"
    )

    return GeneratedDocument(
        template_id=template.id,
        title=template.title,
        body=body,
        citation=citation,
        after=list(template.after),
        missing=missing,
        limitation=list(template.limitation),
        related=list(template.related),
    )


def catalogue() -> list[dict]:
    return [
        {
            "id": t.id,
            "title": t.title,
            "description": t.description,
            "category": t.category,
            "citation": f"{t.act} — {t.section}" if t.section != "—" else "General civil practice",
            "fee": t.fee,
            "fields": [
                {
                    "name": f.name,
                    "label": f.label,
                    "kind": f.kind,
                    "required": f.required,
                    "placeholder": f.placeholder,
                    "help": f.help,
                }
                for f in t.fields
            ],
            "after": list(t.after),
            "limitation": list(t.limitation),
        }
        for t in TEMPLATES.values()
    ]
