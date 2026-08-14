"""
Forum router — which body actually hears this.

Going to the wrong forum is expensive in a way that is invisible until it
happens: months pass, the matter is returned for want of jurisdiction, and by
then limitation may have run. A consumer dispute filed as a civil suit, a
cheque case filed where the drawer lives rather than where the bank branch is,
a service matter taken to a civil court that has no jurisdiction over it.

Given a problem type and, where it matters, the amount at stake, this returns
the forum, what it costs, what to bring, and whether a lawyer is needed. Rules
are data, not prose, so they can be corrected without touching logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field

LAKH = 100_000
CRORE = 10_000_000


@dataclass(frozen=True)
class Forum:
    name: str
    #: Where geographically, in the user's terms.
    where: str
    fee: str
    how_to_file: str
    documents: tuple[str, ...]
    lawyer_needed: str
    typical_duration: str = ""
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class ForumRule:
    id: str
    label: str
    category: str
    #: When set, the claim value decides between tiers.
    value_question: str | None = None
    #: (inclusive upper bound in rupees or None for unbounded, Forum)
    tiers: tuple[tuple[int | None, Forum], ...] = ()
    forum: Forum | None = None
    #: Limitation rule ids in `limitation.py` that apply here.
    limitation: tuple[str, ...] = ()
    #: Corpus passage ids explaining the underlying law.
    related: tuple[str, ...] = ()


_CONSUMER_DOCS = (
    "Invoice or proof of purchase",
    "Warranty or guarantee card, if any",
    "Written complaint sent to the seller and their reply",
    "Photographs or a report evidencing the defect",
    "Proof of payment",
)

RULES: list[ForumRule] = [
    ForumRule(
        id="consumer",
        label="Defective product, deficient service, or a refund refused",
        category="Consumer",
        value_question="What did you pay for the goods or service? (not the compensation you want)",
        tiers=(
            (50 * LAKH, Forum(
                name="District Consumer Disputes Redressal Commission",
                where="The district where you live or work — you no longer have to travel to the seller's city.",
                fee="₹100 to ₹500 depending on value. Nothing at all for claims up to ₹5 lakh.",
                how_to_file="Online at edaakhil.nic.in, or in person at the Commission.",
                documents=_CONSUMER_DOCS,
                lawyer_needed="No. You may argue your own case, and most people do.",
                typical_duration="3 to 9 months where the matter is straightforward.",
                notes=(
                    "Send a written notice to the seller first and keep proof of posting.",
                    "The National Consumer Helpline on 1915 often resolves matters without filing.",
                ),
            )),
            (2 * CRORE, Forum(
                name="State Consumer Disputes Redressal Commission",
                where="Your State capital, usually.",
                fee="₹2,000 approximately, by demand draft.",
                how_to_file="Online at edaakhil.nic.in, or in person.",
                documents=_CONSUMER_DOCS,
                lawyer_needed="Not required, but advisable at this value.",
                typical_duration="9 to 18 months.",
            )),
            (None, Forum(
                name="National Consumer Disputes Redressal Commission",
                where="New Delhi.",
                fee="₹5,000 approximately.",
                how_to_file="Online at edaakhil.nic.in.",
                documents=_CONSUMER_DOCS,
                lawyer_needed="Advisable.",
                typical_duration="1 to 3 years.",
            )),
        ),
        limitation=("consumer_complaint",),
        related=("consumer_where_to_file", "consumer_how_to_file", "e_commerce_rights"),
    ),
    ForumRule(
        id="cheque_bounce",
        label="A cheque given to me bounced",
        category="Money recovery",
        forum=Forum(
            name="Judicial Magistrate First Class",
            where=(
                "The court where the bank branch that returned the cheque is located — "
                "not where the person who gave it to you lives. Filing in the wrong "
                "place is the single most common error in these cases."
            ),
            fee="Nominal court fee, varying by State.",
            how_to_file="A criminal complaint under Section 138 of the Negotiable Instruments Act, 1881.",
            documents=(
                "The original cheque",
                "The bank's dishonour memo or return slip",
                "A copy of your demand notice and the postal receipt",
                "Proof the notice was delivered (tracking or acknowledgement)",
                "Proof of the underlying debt — invoice, agreement, loan record",
            ),
            lawyer_needed="Yes, in practice. This is a criminal complaint with a strict procedure.",
            typical_duration="1 to 2 years, though many settle earlier.",
            notes=(
                "The deadlines are unforgiving and run in sequence. Check both of them.",
                "You can also file a civil suit to recover the money; the two run in parallel.",
            ),
        ),
        limitation=("cheque_notice", "cheque_complaint"),
        related=("cheque_bounce",),
    ),
    ForumRule(
        id="domestic_violence",
        label="Domestic violence, or I need a protection order",
        category="Family",
        forum=Forum(
            name="Judicial Magistrate First Class",
            where="Where you live, where the respondent lives, or where the violence occurred — your choice.",
            fee="None.",
            how_to_file=(
                "Through a Protection Officer, a registered service provider, or by "
                "applying to the Magistrate directly."
            ),
            documents=(
                "Your account of the incidents, with dates as far as you recall them",
                "Medical records, if any",
                "Photographs or messages evidencing the abuse",
                "Proof of the shared household — rent agreement, utility bill, ration card",
            ),
            lawyer_needed="No. Free legal aid is available, and a Protection Officer will assist.",
            typical_duration="An interim protection order can come within days.",
            notes=(
                "You can seek a residence order to stay in the shared household regardless of who owns it.",
                "The Act is civil. You may also file a criminal complaint separately.",
                "Women's helpline: 181. Free legal aid: 15100.",
            ),
        ),
        limitation=("domestic_violence",),
        related=("domestic_violence", "bns_cruelty_husband"),
    ),
    ForumRule(
        id="maintenance",
        label="I need maintenance from a spouse, child or parent",
        category="Family",
        forum=Forum(
            name="Family Court, or the Judicial Magistrate where there is no Family Court",
            where="Where you live, where the other party lives, or where you last lived together.",
            fee="Nominal.",
            how_to_file="An application under Section 144 of the Bharatiya Nagarik Suraksha Sanhita, 2023.",
            documents=(
                "Proof of the relationship — marriage certificate, birth certificate",
                "Evidence of the other party's income, if you have any",
                "Your own income and expenses",
                "Proof of neglect or refusal to maintain",
            ),
            lawyer_needed="Not strictly. Free legal aid covers this.",
            typical_duration="Interim maintenance is often ordered within a few months.",
            notes=(
                "This remedy applies regardless of religion.",
                "Arrears are usually limited to the twelve months before you apply, so delay costs money.",
            ),
        ),
        limitation=("maintenance_claim",),
        related=("maintenance", "shah_bano"),
    ),
    ForumRule(
        id="road_accident",
        label="Compensation after a road accident",
        category="Accident",
        forum=Forum(
            name="Motor Accidents Claims Tribunal",
            where="Where the accident happened, where you live, or where the respondent lives.",
            fee="None.",
            how_to_file="A claim petition under Section 166 of the Motor Vehicles Act, 1988.",
            documents=(
                "Copy of the FIR and the charge sheet if filed",
                "Medical records and bills",
                "Proof of income — salary slips, income tax returns",
                "The offending vehicle's registration and insurance details",
                "Post-mortem report and death certificate, in a fatal case",
                "Disability certificate, where there is lasting injury",
            ),
            lawyer_needed="Advisable. Legal aid is available.",
            typical_duration="1 to 3 years, with interim relief possible earlier.",
            notes=(
                "There is no limitation period since the 2019 amendment.",
                "A no-fault claim of ₹5 lakh for death or ₹2.5 lakh for grievous hurt "
                "needs no proof of negligence.",
                "Hit-and-run victims can claim from the Solatium Fund.",
            ),
        ),
        limitation=("mact_claim",),
        related=("accident_compensation",),
    ),
    ForumRule(
        id="rti_refused",
        label="A public authority refused or ignored my RTI",
        category="Transparency",
        forum=Forum(
            name="First Appellate Authority, then the Information Commission",
            where="The First Appellate Authority sits inside the same department. The second appeal goes to the Central or State Information Commission.",
            fee="None for either appeal.",
            how_to_file="A written appeal. No prescribed form is required.",
            documents=(
                "Copy of your original RTI application",
                "Proof of the fee paid",
                "The reply you received, or proof that 30 days passed with no reply",
            ),
            lawyer_needed="No.",
            typical_duration="First appeal within 30 to 45 days; the Commission takes longer.",
            notes=(
                "An officer who refuses without reasonable cause is liable to ₹250 per day, "
                "up to ₹25,000. Ask for that penalty expressly in your appeal.",
            ),
        ),
        limitation=("rti_first_appeal", "rti_second_appeal"),
        related=("rti_appeals", "rti_exemptions"),
    ),
    ForumRule(
        id="cyber_fraud",
        label="I was defrauded online, or money left my account",
        category="Cyber",
        forum=Forum(
            name="National Cyber Crime Reporting Portal, and your bank",
            where="Online at cybercrime.gov.in, or the Cyber Crime Police Station in your district.",
            fee="None.",
            how_to_file="Report on the portal or call 1930. Notify the bank in writing the same day.",
            documents=(
                "Transaction reference numbers and bank statement",
                "Screenshots showing the URL, sender number or email headers",
                "Any call or message from the fraudster — do not delete them",
                "Your written intimation to the bank, with its acknowledgement",
            ),
            lawyer_needed="No, to report. Yes, if you later sue the bank.",
            typical_duration="A freeze on the money is possible within hours if you report immediately.",
            notes=(
                "Speed decides the outcome. Report within three working days and your "
                "liability is zero where the fault is not yours.",
                "If the bank does not resolve it in 30 days, escalate to the RBI Ombudsman "
                "at cms.rbi.org.in — that is free.",
            ),
        ),
        related=("cybercrime_reporting", "banking_fraud_liability"),
    ),
    ForumRule(
        id="unpaid_salary",
        label="My employer has not paid my salary or dues",
        category="Work",
        forum=Forum(
            name="Authority appointed under the Code on Wages",
            where="The area where you were employed.",
            fee="None.",
            how_to_file="A claim application. An inspector-cum-facilitator can also file on your behalf.",
            documents=(
                "Appointment letter or contract",
                "Salary slips, and bank statements showing what was paid",
                "Attendance records if you have them",
                "Any written demand you made and the reply",
            ),
            lawyer_needed="No.",
            typical_duration="Months rather than years.",
            notes=(
                "The authority can order up to ten times the withheld amount as compensation.",
                "Final dues are payable within two working days of leaving.",
            ),
        ),
        limitation=("wages_claim",),
        related=("wage_theft", "labour_codes"),
    ),
    ForumRule(
        id="workplace_harassment",
        label="I was sexually harassed at work",
        category="Work",
        forum=Forum(
            name="Internal Committee, or the Local Committee",
            where=(
                "The Internal Committee at your workplace, if it employs ten or more people. "
                "Where there is none, or the complaint is against the employer, the Local "
                "Committee constituted by the District Officer."
            ),
            fee="None.",
            how_to_file="A written complaint in six copies, with supporting documents and witness names.",
            documents=(
                "A dated account of the incidents",
                "Messages, emails or call records",
                "Names and contact details of any witnesses",
            ),
            lawyer_needed="No. The Committee assists you through the process.",
            typical_duration="The inquiry must be completed within 90 days.",
            notes=(
                "You may request interim relief — transfer, leave, or restraining the "
                "respondent from reporting on your work — while the inquiry runs.",
                "Your identity must not be published.",
                "A criminal complaint under the Bharatiya Nyaya Sanhita is a separate, parallel option.",
            ),
        ),
        limitation=("posh_complaint",),
        related=("vishaka_posh",),
    ),
    ForumRule(
        id="landlord_tenant",
        label="A dispute with my landlord or tenant",
        category="Property",
        forum=Forum(
            name="Rent Authority or Rent Court under your State's rent law",
            where="The district where the property is.",
            fee="Nominal, set by State rules.",
            how_to_file="An application under the State rent legislation. Several States follow the Model Tenancy Act, 2021.",
            documents=(
                "The rent agreement",
                "Rent receipts or bank transfer records",
                "Proof of the security deposit paid",
                "Photographs, where the dispute is about the condition of the property",
                "Any notice exchanged between you",
            ),
            lawyer_needed="Not usually.",
            typical_duration="Under the Model Act, 60 days is the target.",
            notes=(
                "A landlord cannot cut off water or electricity, and cannot evict without an order.",
                "The security deposit is capped at two months' rent for residential premises "
                "in States that have adopted the Model Act.",
            ),
        ),
        # A deposit the landlord will not return is a money claim, and the
        # three-year clock under Article 55 runs whether or not the State has a
        # Rent Authority to hear it. Leaving this empty meant the one dispute
        # people actually bring here carried no deadline at all.
        limitation=("suit_money",),
        related=("tenant_rights", "deposit_recovery"),
    ),
    ForumRule(
        id="police_inaction",
        label="The police will not register my FIR",
        category="Police",
        forum=Forum(
            name="Superintendent of Police, then the Judicial Magistrate",
            where="The SP for the district. Failing that, the Magistrate having jurisdiction.",
            fee="None.",
            how_to_file=(
                "Send your written complaint to the SP by registered post. If that fails, "
                "apply to the Magistrate under Section 175(3) of the BNSS, 2023."
            ),
            documents=(
                "Your written complaint",
                "The postal receipt and tracking record — this proves the date you tried",
                "Any acknowledgement from the police station",
                "Evidence of the offence itself",
            ),
            lawyer_needed="No for the SP complaint. Helpful for the Magistrate application.",
            typical_duration="The SP route can produce an FIR within weeks.",
            notes=(
                "A station cannot refuse on the ground that the offence happened elsewhere — "
                "that is what a Zero FIR is for.",
                "Refusing to record information about certain offences against women is "
                "itself an offence by the officer.",
            ),
        ),
        related=("fir_refusal_remedy", "zero_fir", "police_complaint_against"),
    ),
    ForumRule(
        id="senior_citizen",
        label="My children will not look after me",
        category="Family",
        forum=Forum(
            name="Maintenance Tribunal for senior citizens",
            where="The subdivision where you live.",
            fee="None.",
            how_to_file="An application under the Maintenance and Welfare of Parents and Senior Citizens Act, 2007.",
            documents=(
                "Proof of age",
                "Proof of relationship to the child or relative",
                "The property transfer deed, if you transferred property to them",
                "Your income and expenses",
            ),
            lawyer_needed="No — lawyers are expressly barred from appearing, to keep it simple and quick.",
            typical_duration="The Tribunal must decide within 90 days.",
            notes=(
                "Where you transferred property on condition of being cared for and they "
                "did not, the transfer can be declared void and possession restored.",
            ),
        ),
        related=("senior_citizens_maintenance",),
    ),
    ForumRule(
        id="insurance_rejected",
        label="My insurance claim was rejected or delayed",
        category="Consumer",
        forum=Forum(
            name="Insurance Ombudsman",
            where="The Ombudsman office for your region.",
            fee="None.",
            how_to_file=(
                "Complain to the insurer's grievance cell first. If unresolved after 30 days, "
                "file with the Ombudsman, or on the IRDAI Bima Bharosa portal."
            ),
            documents=(
                "The policy document",
                "The claim form and everything you submitted with it",
                "The insurer's rejection letter",
                "Your complaint to the grievance cell and its reply",
                "Medical or repair records, as applicable",
            ),
            lawyer_needed="No.",
            typical_duration="The Ombudsman aims to decide within three months.",
            notes=(
                "The Ombudsman handles claims up to ₹50 lakh and its award binds the insurer.",
                "A life policy cannot be repudiated for misstatement after three years — "
                "Section 45 of the Insurance Act is an absolute bar.",
                "A consumer commission is an alternative route.",
            ),
        ),
        limitation=("consumer_complaint",),
        related=("insurance_claim_rejected",),
    ),
]

BY_ID: dict[str, ForumRule] = {r.id: r for r in RULES}


@dataclass
class ForumResult:
    rule_id: str
    label: str
    forum: dict
    #: Applicable limitation rules, resolved for the UI to offer next.
    limitation: list[dict] = field(default_factory=list)
    related: list[str] = field(default_factory=list)
    value_tier: str | None = None


def _forum_dict(forum: Forum) -> dict:
    return {
        "name": forum.name,
        "where": forum.where,
        "fee": forum.fee,
        "how_to_file": forum.how_to_file,
        "documents": list(forum.documents),
        "lawyer_needed": forum.lawyer_needed,
        "typical_duration": forum.typical_duration,
        "notes": list(forum.notes),
    }


def route(rule_id: str, claim_value: float | None = None) -> ForumResult:
    """Resolve a problem to its forum, using the claim value where it matters."""
    rule = BY_ID.get(rule_id)
    if rule is None:
        raise KeyError(f"Unknown forum rule: {rule_id}")

    from .limitation import BY_ID as LIMITATION_BY_ID

    tier_label: str | None = None
    if rule.tiers:
        value = claim_value if claim_value is not None else 0.0
        chosen = rule.tiers[-1][1]
        for upper, forum in rule.tiers:
            if upper is None or value <= upper:
                chosen = forum
                if upper is None:
                    tier_label = "above ₹2 crore"
                elif upper >= CRORE:
                    tier_label = f"up to ₹{upper / CRORE:g} crore"
                else:
                    tier_label = f"up to ₹{upper / LAKH:g} lakh"
                break
    else:
        chosen = rule.forum  # type: ignore[assignment]

    limitation = [
        {
            "id": lid,
            "label": LIMITATION_BY_ID[lid].label,
            "trigger": LIMITATION_BY_ID[lid].trigger,
        }
        for lid in rule.limitation
        if lid in LIMITATION_BY_ID
    ]

    return ForumResult(
        rule_id=rule.id,
        label=rule.label,
        forum=_forum_dict(chosen),
        limitation=limitation,
        related=list(rule.related),
        value_tier=tier_label,
    )


def catalogue() -> list[dict]:
    return [
        {
            "id": r.id,
            "label": r.label,
            "category": r.category,
            "value_question": r.value_question,
        }
        for r in RULES
    ]
