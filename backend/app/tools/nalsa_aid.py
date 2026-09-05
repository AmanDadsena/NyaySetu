"""
NALSA Legal Aid & Tele-Law Eligibility Evaluator.

Statutory evaluation under Section 12 of the Legal Services Authorities Act, 1987.
Identifies whether an Indian citizen qualifies for free legal services, assigned counsel,
and court fee exemptions across District Legal Services Authorities (DLSA),
High Court Legal Services Committees (HCLSC), and the Supreme Court Legal Services Committee (SCLSC).
"""

from dataclasses import dataclass
from typing import List, Optional

# State-notified annual income thresholds under Section 12(h) for Subordinate & District courts
STATE_INCOME_LIMITS: dict[str, float] = {
    "delhi": 300000.0,
    "maharashtra": 300000.0,
    "karnataka": 300000.0,
    "tamil nadu": 300000.0,
    "telangana": 300000.0,
    "andhra pradesh": 300000.0,
    "west bengal": 150000.0,
    "uttar pradesh": 100000.0,
    "bihar": 150000.0,
    "rajasthan": 150000.0,
    "madhya pradesh": 150000.0,
    "gujarat": 150000.0,
    "kerala": 300000.0,
    "punjab": 150000.0,
    "haryana": 150000.0,
    "odisha": 150000.0,
    "assam": 150000.0,
    "chhattisgarh": 150000.0,
    "jharkhand": 150000.0,
}

DEFAULT_DISTRICT_INCOME_LIMIT = 150000.0
HIGH_COURT_INCOME_LIMIT = 300000.0
SUPREME_COURT_INCOME_LIMIT = 500000.0


@dataclass
class LegalAidAssessment:
    eligible: bool
    category: str
    statutory_clause: str
    income_limit_applied: Optional[float]
    entitlements: List[str]
    action_steps: List[str]
    helpline: str
    portal_url: str


def evaluate_legal_aid(
    *,
    is_woman_or_child: bool = False,
    is_sc_st: bool = False,
    is_disabled: bool = False,
    is_industrial_workman: bool = False,
    is_in_custody: bool = False,
    is_disaster_victim: bool = False,
    annual_income: float = 0.0,
    state: str = "default",
    court_level: str = "district",
) -> LegalAidAssessment:
    """
    Evaluate eligibility under Section 12 of the Legal Services Authorities Act, 1987.
    """
    entitlements = [
        "Free legal representation by an empaneled legal aid advocate",
        "Payment of court fees, process fees, and advocate drafting charges",
        "Free certified copies of orders, judgments, and deposition transcripts",
        "Pre-litigation mediation and settlement through Lok Adalat",
    ]

    action_steps = [
        "Visit the District Legal Services Authority (DLSA) office located within your district court complex",
        "Alternatively, visit your nearest Common Service Centre (CSC) to register via the Tele-Law portal",
        "Carry identity proof (Aadhaar/Voter ID) and supporting category certificate (or income certificate if applying under income criteria)",
        "Call the National Legal Services Authority toll-free helpline at 15100 for immediate procedural assistance",
    ]

    helpline = "15100 (NALSA 24x7 National Legal Aid Toll-Free Helpline)"
    portal_url = "https://nalsa.gov.in and https://www.tele-law.in"

    # ── Category 1: Categorical Entitlements (Zero Income Barrier) ──
    if is_woman_or_child:
        return LegalAidAssessment(
            eligible=True,
            category="Woman or Child",
            statutory_clause="Section 12(c), Legal Services Authorities Act, 1987",
            income_limit_applied=None,
            entitlements=entitlements,
            action_steps=action_steps,
            helpline=helpline,
            portal_url=portal_url,
        )

    if is_sc_st:
        return LegalAidAssessment(
            eligible=True,
            category="Scheduled Caste / Scheduled Tribe",
            statutory_clause="Section 12(a), Legal Services Authorities Act, 1987",
            income_limit_applied=None,
            entitlements=entitlements,
            action_steps=action_steps,
            helpline=helpline,
            portal_url=portal_url,
        )

    if is_disabled:
        return LegalAidAssessment(
            eligible=True,
            category="Person with Disability",
            statutory_clause="Section 12(d), Legal Services Authorities Act, 1987 read with Rights of Persons with Disabilities Act, 2016",
            income_limit_applied=None,
            entitlements=entitlements,
            action_steps=action_steps,
            helpline=helpline,
            portal_url=portal_url,
        )

    if is_industrial_workman:
        return LegalAidAssessment(
            eligible=True,
            category="Industrial Workman",
            statutory_clause="Section 12(f), Legal Services Authorities Act, 1987",
            income_limit_applied=None,
            entitlements=entitlements,
            action_steps=action_steps,
            helpline=helpline,
            portal_url=portal_url,
        )

    if is_in_custody:
        return LegalAidAssessment(
            eligible=True,
            category="Person in Custody / Undertrial Prisoner",
            statutory_clause="Section 12(g), Legal Services Authorities Act, 1987",
            income_limit_applied=None,
            entitlements=entitlements,
            action_steps=action_steps,
            helpline=helpline,
            portal_url=portal_url,
        )

    if is_disaster_victim:
        return LegalAidAssessment(
            eligible=True,
            category="Victim of Disaster / Ethnic Violence / Caste Atrocity",
            statutory_clause="Section 12(e), Legal Services Authorities Act, 1987",
            income_limit_applied=None,
            entitlements=entitlements,
            action_steps=action_steps,
            helpline=helpline,
            portal_url=portal_url,
        )

    # ── Category 2: Income-Based Entitlement under Section 12(h) ──
    clean_court = court_level.strip().lower()
    clean_state = state.strip().lower()

    if "supreme" in clean_court:
        limit = SUPREME_COURT_INCOME_LIMIT
        court_name = "Supreme Court (SCLSC)"
    elif "high" in clean_court:
        limit = HIGH_COURT_INCOME_LIMIT
        court_name = "High Court (HCLSC)"
    else:
        limit = STATE_INCOME_LIMITS.get(clean_state, DEFAULT_DISTRICT_INCOME_LIMIT)
        court_name = f"District / Subordinate Courts in {state.title() if state != 'default' else 'State'}"

    if annual_income <= limit:
        return LegalAidAssessment(
            eligible=True,
            category=f"Income Criterion Satisfied ({court_name})",
            statutory_clause="Section 12(h), Legal Services Authorities Act, 1987",
            income_limit_applied=limit,
            entitlements=entitlements,
            action_steps=action_steps,
            helpline=helpline,
            portal_url=portal_url,
        )

    # Not eligible under statutory criteria
    return LegalAidAssessment(
        eligible=False,
        category="Income Above Prescribed Statutory Threshold",
        statutory_clause="Section 12(h), Legal Services Authorities Act, 1987",
        income_limit_applied=limit,
        entitlements=[],
        action_steps=[
            f"Your declared annual income (₹{annual_income:,.0f}) exceeds the statutory threshold of ₹{limit:,.0f} for {court_name}.",
            "If your income has decreased due to recent job loss, medical emergency, or unforeseen liabilities, obtain an updated income certificate from the Tahsildar/Revenue Officer.",
            "You may still avail of dispute resolution and pre-litigation settlement through Lok Adalat, which does not require legal aid qualification.",
            "Contact a private legal counsel or the local Bar Association for representation.",
        ],
        helpline=helpline,
        portal_url=portal_url,
    )
