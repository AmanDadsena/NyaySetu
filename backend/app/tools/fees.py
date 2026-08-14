"""
Court and filing fee calculator.

Court fees on civil suits are a State subject. Every State has its own Court
Fees Act with its own slabs, and the ad valorem rate changes several times as
the claim value rises — which is why looking it up is tedious and why people
get it wrong. An under-stamped plaint is returned for deficit, costing weeks.

Two kinds of fee are modelled:

  * **Fixed or centrally prescribed** — consumer commissions, RTI, tribunals.
    These are the same across India and can be stated exactly.

  * **Ad valorem, State-specific** — civil suits. A representative slab table
    is provided for a few States, and the answer is explicitly labelled an
    estimate, because it is. Anyone filing should confirm against their State's
    schedule or ask the filing counter.

Saying "approximately ₹X, confirm locally" is more honest and more useful than
either silence or a confident number that may be wrong by a factor of two.
"""

from __future__ import annotations

from dataclasses import dataclass, field

LAKH = 100_000
CRORE = 10_000_000


@dataclass
class FeeResult:
    forum: str
    amount: str
    exact: bool
    basis: str
    authority: str
    notes: list[str] = field(default_factory=list)
    #: Other costs people forget to budget for.
    additional: list[str] = field(default_factory=list)


def _rupees(value: float) -> str:
    """Indian digit grouping."""
    whole = int(round(value))
    digits = str(abs(whole))
    if len(digits) > 3:
        last3, rest = digits[-3:], digits[:-3]
        groups = []
        while len(rest) > 2:
            groups.insert(0, rest[-2:])
            rest = rest[:-2]
        if rest:
            groups.insert(0, rest)
        digits = ",".join(groups + [last3])
    return f"₹{digits}"


# ── Fixed and centrally prescribed ──────────────────────────────────────
def _consumer(value: float) -> FeeResult:
    if value <= 5 * LAKH:
        amount, note = "No fee", "Claims up to ₹5 lakh are exempt from fee entirely."
    elif value <= 10 * LAKH:
        amount, note = "₹200", ""
    elif value <= 20 * LAKH:
        amount, note = "₹400", ""
    elif value <= 50 * LAKH:
        amount, note = "₹1,000", ""
    elif value <= 1 * CRORE:
        amount, note = "₹2,000", ""
    elif value <= 2 * CRORE:
        amount, note = "₹2,500", "Filed before the State Commission."
    elif value <= 4 * CRORE:
        amount, note = "₹3,000", "Filed before the National Commission."
    elif value <= 10 * CRORE:
        amount, note = "₹6,000", "Filed before the National Commission."
    else:
        amount, note = "₹7,500", "Filed before the National Commission."

    return FeeResult(
        forum="Consumer Disputes Redressal Commission",
        amount=amount,
        exact=True,
        basis="Fee slab based on the value of the goods or services paid for, "
              "not the compensation claimed.",
        authority="Consumer Protection (Consumer Disputes Redressal Commissions) Rules, 2020",
        notes=[n for n in [note] if n],
        additional=[
            "Payable by demand draft or through edaakhil.nic.in.",
            "No advocate is required, so there need be no professional fee at all.",
        ],
    )


def _rti(_: float) -> FeeResult:
    return FeeResult(
        forum="Right to Information application",
        amount="₹10",
        exact=True,
        basis="Flat application fee.",
        authority="Right to Information (Regulation of Fee and Cost) Rules, 2005",
        notes=[
            "Nothing at all if you hold a Below Poverty Line card.",
            "Both the first and second appeals are free.",
            "If the reply is late, the information must be supplied free of cost "
            "under Section 7(6).",
        ],
        additional=[
            "₹2 per A4 page for photocopies.",
            "₹50 per floppy or CD, where records are supplied electronically.",
            "Inspection of records is free for the first hour, then ₹5 per 15 minutes.",
        ],
    )


def _mact(_: float) -> FeeResult:
    return FeeResult(
        forum="Motor Accidents Claims Tribunal",
        amount="No fee",
        exact=True,
        basis="Claim petitions are exempt.",
        authority="Motor Vehicles Act, 1988",
        notes=["There is also no limitation period since the 2019 amendment."],
        additional=["Legal aid is available if you cannot afford an advocate — call 15100."],
    )


def _family(_: float) -> FeeResult:
    return FeeResult(
        forum="Family Court",
        amount="₹15 to ₹100",
        exact=False,
        basis="A nominal fixed fee, set by State rules.",
        authority="Family Courts Act, 1984, read with State court fee rules",
        notes=["Maintenance applications under Section 144 BNSS attract only a nominal fee."],
        additional=["Certified copies are charged per page."],
    )


def _cheque(_: float) -> FeeResult:
    return FeeResult(
        forum="Judicial Magistrate — Section 138 complaint",
        amount="₹20 to ₹200",
        exact=False,
        basis="A nominal process fee, set by State rules.",
        authority="State court fee legislation",
        notes=[
            "The fee is trivial. The cost that matters is the advocate's, and the "
            "deadlines, which are unforgiving."
        ],
        additional=["Process fee per accused for issuing summons."],
    )


def _tribunal(_: float) -> FeeResult:
    return FeeResult(
        forum="Central or State Administrative Tribunal",
        amount="₹50",
        exact=True,
        basis="Flat application fee for service matters.",
        authority="Administrative Tribunals (Procedure) Rules, 1987",
        additional=["No fee for an application to condone delay."],
    )


# ── Ad valorem, State-specific ──────────────────────────────────────────
#: (upper bound of slab, rate as a fraction, flat addition)
#: Representative only — confirm against the State schedule before filing.
_CIVIL_SLABS: dict[str, tuple[str, tuple[tuple[float | None, float, float], ...], float]] = {
    "maharashtra": ("Maharashtra Court Fees Act, 1959", (
        (5_000, 0.0, 100),
        (50_000, 0.03, 0),
        (5 * LAKH, 0.04, 0),
        (10 * LAKH, 0.05, 0),
        (None, 0.06, 0),
    ), 3 * LAKH),
    "delhi": ("Court Fees Act, 1870 as applicable to Delhi", (
        (5_000, 0.0, 100),
        (50_000, 0.04, 0),
        (5 * LAKH, 0.05, 0),
        (None, 0.06, 0),
    ), 2 * LAKH),
    "karnataka": ("Karnataka Court Fees and Suits Valuation Act, 1958", (
        (5_000, 0.0, 100),
        (1 * LAKH, 0.04, 0),
        (10 * LAKH, 0.05, 0),
        (None, 0.06, 0),
    ), 2 * LAKH),
    "tamil_nadu": ("Tamil Nadu Court Fees and Suits Valuation Act, 1955", (
        (5_000, 0.0, 100),
        (1 * LAKH, 0.05, 0),
        (None, 0.075, 0),
    ), 1.5 * LAKH),
    "uttar_pradesh": ("Court Fees Act, 1870 as applicable to Uttar Pradesh", (
        (5_000, 0.0, 100),
        (50_000, 0.05, 0),
        (None, 0.075, 0),
    ), 2 * LAKH),
}

STATES = [
    {"id": "maharashtra", "label": "Maharashtra"},
    {"id": "delhi", "label": "Delhi"},
    {"id": "karnataka", "label": "Karnataka"},
    {"id": "tamil_nadu", "label": "Tamil Nadu"},
    {"id": "uttar_pradesh", "label": "Uttar Pradesh"},
]


def _civil_suit(value: float, state: str | None) -> FeeResult:
    key = (state or "").lower().replace(" ", "_")
    if key not in _CIVIL_SLABS:
        return FeeResult(
            forum="Civil Court",
            amount="Varies by State",
            exact=False,
            basis="Court fees on civil suits are ad valorem and set by each State.",
            authority="State Court Fees Act",
            notes=[
                "Select a State to get an estimate, or ask the filing counter of the "
                "court where you intend to file — they will tell you exactly.",
            ],
        )

    authority, slabs, cap = _CIVIL_SLABS[key]
    fee = 0.0
    for upper, rate, flat in slabs:
        if flat:
            fee = flat
        else:
            fee = value * rate
        if upper is None or value <= upper:
            break

    capped = min(fee, cap)
    hit_cap = capped < fee

    notes = [
        "This is an estimate. Slabs and rates change, and several States apply "
        "different rates to different kinds of relief — confirm against your "
        "State's schedule before you file.",
        "An under-stamped plaint is returned for deficit court fee, which costs weeks.",
    ]
    if hit_cap:
        notes.insert(0, f"The State caps court fee at {_rupees(cap)}, which applies here.")

    return FeeResult(
        forum="Civil Court",
        amount=f"approximately {_rupees(capped)}",
        exact=False,
        basis="Ad valorem on the value of the suit.",
        authority=authority,
        notes=notes,
        additional=[
            "Process fee for serving each defendant.",
            "Vakalatnama stamp, where an advocate appears.",
            "Advocate's professional fee — usually far larger than the court fee.",
        ],
    )


_CALCULATORS = {
    "consumer": _consumer,
    "rti": _rti,
    "mact": _mact,
    "family": _family,
    "cheque": _cheque,
    "tribunal": _tribunal,
}

MATTERS = [
    {"id": "consumer", "label": "Consumer complaint", "needs_value": True, "needs_state": False},
    {"id": "civil_suit", "label": "Civil suit (recovery, title, injunction)", "needs_value": True, "needs_state": True},
    {"id": "cheque", "label": "Cheque bounce complaint", "needs_value": False, "needs_state": False},
    {"id": "family", "label": "Family court matter", "needs_value": False, "needs_state": False},
    {"id": "mact", "label": "Motor accident claim", "needs_value": False, "needs_state": False},
    {"id": "rti", "label": "RTI application", "needs_value": False, "needs_state": False},
    {"id": "tribunal", "label": "Service matter before a Tribunal", "needs_value": False, "needs_state": False},
]


def calculate(matter: str, value: float = 0.0, state: str | None = None) -> FeeResult:
    if matter == "civil_suit":
        return _civil_suit(value, state)
    calculator = _CALCULATORS.get(matter)
    if calculator is None:
        raise KeyError(f"Unknown fee matter: {matter}")
    return calculator(value)


def catalogue() -> dict:
    return {"matters": MATTERS, "states": STATES}
