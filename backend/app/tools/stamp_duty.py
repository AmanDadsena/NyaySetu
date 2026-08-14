"""
Stamp duty and registration fee estimator.

Stamp duty is a State subject for most instruments, so there is no national
rate, and the rates move with every State budget. What makes people lose money
here is not the arithmetic — it is two things they are not told:

  * Duty is charged on the **higher** of the consideration written into the
    deed and the State's circle rate / ready reckoner / guidance value. Writing
    a lower price into the deed does not lower the duty; it produces a deficit
    notice under Section 47-A of the Indian Stamp Act, plus penalty.

  * Several States charge women buyers less. It is not applied automatically by
    anyone — the concession has to be claimed, and the property has to be in
    her name for it.

So the tool reports a band, names the ready-reckoner problem before the number,
and states the concession where one exists. Every ad valorem figure is labelled
an estimate, because it is: the rate table below is representative, not the
notified schedule of any particular sub-registrar on any particular day.

Same discipline as `fees.py`: an honest "approximately ₹X, and here is what
changes it" beats a confident number that is wrong by a percentage point on a
sum this large.
"""

from __future__ import annotations

from dataclasses import dataclass, field

LAKH = 100_000
CRORE = 10_000_000


@dataclass
class StampDutyResult:
    instrument: str
    #: Headline duty, already formatted.
    duty: str
    registration_fee: str
    total: str
    exact: bool
    #: The value the duty was actually computed on.
    charged_on: str
    basis: str
    authority: str
    #: Set where a women's-buyer or similar concession changed the number.
    concession: str = ""
    #: What the concession would have been worth, had it applied.
    concession_forgone: str = ""
    notes: list[str] = field(default_factory=list)
    additional: list[str] = field(default_factory=list)


def _rupees(value: float) -> str:
    """Indian digit grouping — ₹8,50,000, not ₹850,000."""
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


# ── Conveyance rates by State ───────────────────────────────────────────
#: Per State: (authority, standard rate, women's rate, women's rebate cap,
#:             registration rate, registration cap, notes)
#:
#: `women_rate` equal to `standard` means that State gives no gender
#: concession — stated explicitly rather than left for the user to infer from
#: an unchanged number.
@dataclass(frozen=True)
class StateRule:
    label: str
    authority: str
    #: Flat rate, or None where the State uses slabs (see `slabs`).
    standard: float | None
    women: float | None
    #: Absolute cap on the women's rebate, where the State caps it (UP).
    women_rebate_cap: float | None
    registration: float
    registration_cap: float | None
    #: (upper bound inclusive, rate) — used where `standard` is None.
    slabs: tuple[tuple[float | None, float], ...] = ()
    notes: tuple[str, ...] = ()


STATE_RULES: dict[str, StateRule] = {
    "maharashtra": StateRule(
        label="Maharashtra",
        authority="Maharashtra Stamp Act, 1958 — Schedule I, Article 25",
        standard=0.06,
        women=0.05,
        women_rebate_cap=None,
        registration=0.01,
        registration_cap=30_000,
        notes=(
            "6% shown here includes the 1% metro cess levied in Mumbai, Pune, "
            "Nagpur and Thane. Outside those cities the rate is generally 5%, "
            "so the estimate is high by 1% for a rural or small-town property.",
            "The 1% women's concession applies to residential property held in "
            "a woman's name, whether solely or jointly with another woman.",
        ),
    ),
    "delhi": StateRule(
        label="Delhi",
        authority="Indian Stamp Act, 1899 as applicable to Delhi",
        standard=0.06,
        women=0.04,
        women_rebate_cap=None,
        registration=0.01,
        registration_cap=None,
        notes=(
            "Delhi's concession is the largest in the country — two full "
            "percentage points. A property bought jointly by a man and a woman "
            "is charged 5%, midway between the two rates.",
        ),
    ),
    "karnataka": StateRule(
        label="Karnataka",
        authority="Karnataka Stamp Act, 1957 — Article 20",
        standard=None,
        women=None,
        women_rebate_cap=None,
        registration=0.01,
        registration_cap=None,
        slabs=(
            (20 * LAKH, 0.02),
            (45 * LAKH, 0.03),
            (None, 0.05),
        ),
        notes=(
            "Karnataka charges by slab rather than a single rate: 2% up to "
            "₹20 lakh, 3% from ₹21 to ₹45 lakh, and 5% above that.",
            "Karnataka offers no separate rate for women buyers.",
            "A cess and surcharge — commonly 10% and 2% to 3% of the duty — "
            "are levied on top and are not included in the figure above.",
        ),
    ),
    "tamil_nadu": StateRule(
        label="Tamil Nadu",
        authority="Indian Stamp Act, 1899 as applicable to Tamil Nadu",
        standard=0.07,
        women=0.07,
        women_rebate_cap=None,
        registration=0.04,
        registration_cap=None,
        notes=(
            "Tamil Nadu's registration fee is 4%, not the 1% most States "
            "charge, so the total cost of transfer is among the highest in "
            "India at roughly 11%. Budget for it.",
            "Tamil Nadu offers no separate rate for women buyers.",
        ),
    ),
    "uttar_pradesh": StateRule(
        label="Uttar Pradesh",
        authority="Indian Stamp Act, 1899 as applicable to Uttar Pradesh",
        standard=0.07,
        women=0.06,
        women_rebate_cap=10_000,
        registration=0.01,
        registration_cap=30_000,
        notes=(
            "The women's concession in Uttar Pradesh is 1%, but capped — it "
            "applies only to the first ₹10 lakh of consideration, so it is "
            "worth at most ₹10,000 however expensive the property.",
        ),
    ),
}

STATES = [{"id": key, "label": rule.label} for key, rule in STATE_RULES.items()]


def _conveyance_rate(rule: StateRule, value: float, buyer: str) -> tuple[float, float]:
    """Return (applicable rate, standard rate) for this buyer and value."""
    if rule.slabs:
        standard = rule.slabs[-1][1]
        for upper, rate in rule.slabs:
            if upper is None or value <= upper:
                standard = rate
                break
        return standard, standard  # slab States give no gender concession

    standard = rule.standard or 0.0
    if buyer == "woman" and rule.women is not None:
        return rule.women, standard
    if buyer == "joint" and rule.women is not None and rule.women != standard:
        # Where a man and a woman buy together, States that differentiate
        # generally charge the midpoint.
        return (rule.women + standard) / 2, standard
    return standard, standard


def _conveyance(
    value: float,
    circle_rate: float,
    state: str | None,
    buyer: str,
    instrument_label: str,
    multiplier: float = 1.0,
    extra_notes: tuple[str, ...] = (),
) -> StampDutyResult:
    """
    Ad valorem duty on a transfer of immovable property.

    `multiplier` scales the conveyance rate for instruments charged as a
    fraction of it — a mortgage, for instance.
    """
    key = (state or "").lower().replace(" ", "_")
    rule = STATE_RULES.get(key)

    # Duty is charged on the higher of the two, always. This is the single
    # most common and most expensive misunderstanding in the whole process.
    chargeable = max(value, circle_rate)
    undervalued = circle_rate > value > 0

    if rule is None:
        return StampDutyResult(
            instrument=instrument_label,
            duty="Varies by State",
            registration_fee="Varies by State",
            total="Varies by State",
            exact=False,
            charged_on=_rupees(chargeable) if chargeable else "—",
            basis="Stamp duty on immovable property is set by each State.",
            authority="State Stamp Act",
            notes=[
                "Select a State for an estimate, or ask the sub-registrar's "
                "office where the property falls — they will tell you the "
                "current rate and it costs nothing to ask.",
            ],
        )

    rate, standard_rate = _conveyance_rate(rule, chargeable, buyer)
    duty = chargeable * rate * multiplier

    # A capped concession (UP) is a rebate on the first slice, not a lower
    # rate throughout — so compute it as the State actually does.
    concession = ""
    forgone = ""
    if rate < standard_rate:
        saved = chargeable * (standard_rate - rate) * multiplier
        if rule.women_rebate_cap is not None:
            saved = min(saved, rule.women_rebate_cap)
            duty = chargeable * standard_rate * multiplier - saved
        label = "in a woman's name" if buyer == "woman" else "jointly, with a woman"
        concession = (
            f"Held {label}, so {rule.label} charges "
            f"{rate * 100:.4g}% instead of {standard_rate * 100:.4g}% — "
            f"a saving of {_rupees(saved)}."
        )
    elif buyer in {"woman", "joint"}:
        # Said explicitly rather than left to be inferred from an unchanged
        # number — a buyer who expects a concession should learn there is none
        # here, not wonder whether the tool forgot to apply it.
        concession = f"{rule.label} charges women buyers the same rate as anyone else."
    elif buyer == "man" and rule.women is not None and rule.women < standard_rate:
        forgone = _rupees(chargeable * (standard_rate - rule.women) * multiplier)
        if rule.women_rebate_cap is not None:
            forgone = _rupees(min(
                chargeable * (standard_rate - rule.women) * multiplier,
                rule.women_rebate_cap,
            ))

    registration = chargeable * rule.registration
    if rule.registration_cap is not None:
        registration = min(registration, rule.registration_cap)

    notes = list(rule.notes)
    if undervalued:
        notes.insert(0, (
            f"The consideration you entered ({_rupees(value)}) is below the "
            f"circle rate ({_rupees(circle_rate)}), so duty has been computed "
            f"on the circle rate. Writing the lower figure into the deed does "
            f"not reduce the duty — it invites a deficit notice under Section "
            f"47-A, with penalty, and can attract income tax on the difference "
            f"in the hands of both buyer and seller."
        ))
    elif circle_rate == 0:
        notes.insert(0, (
            "Duty is charged on the higher of the price and the State's circle "
            "rate for that locality. Enter the circle rate if you know it — "
            "otherwise this figure assumes the price is the higher of the two."
        ))
    if rule.registration_cap is not None:
        notes.append(
            f"{rule.label} caps the registration fee at "
            f"{_rupees(rule.registration_cap)}."
        )
    notes.extend(extra_notes)

    return StampDutyResult(
        instrument=instrument_label,
        duty=f"approximately {_rupees(duty)}",
        registration_fee=f"approximately {_rupees(registration)}",
        total=f"approximately {_rupees(duty + registration)}",
        exact=False,
        charged_on=_rupees(chargeable),
        basis=(
            f"{rate * 100:.4g}% of the chargeable value"
            + (f", being {multiplier * 100:.4g}% of the conveyance rate" if multiplier != 1.0 else "")
            + f", plus a registration fee of {rule.registration * 100:.4g}%."
        ),
        authority=rule.authority,
        concession=concession,
        concession_forgone=forgone,
        notes=notes,
        additional=[
            "Sub-registrar's scanning and handling charges, usually a few "
            "hundred rupees.",
            "Advocate's or deed-writer's fee for drafting the instrument.",
            "Where a broker is involved, brokerage is separate and negotiable.",
            "One percent TDS under Section 194-IA where the consideration is "
            "₹50 lakh or more, deducted by the buyer and deposited against "
            "the seller's PAN.",
        ],
    )


def _gift(value: float, circle_rate: float, state: str | None, buyer: str) -> StampDutyResult:
    result = _conveyance(
        value, circle_rate, state, buyer, "Gift deed",
        extra_notes=(
            "Several States charge a concessional or nominal duty where the "
            "gift is to a close relative — spouse, child, parent, sibling or "
            "grandchild. Maharashtra charges ₹200 on a residential gift to a "
            "spouse, child or grandchild; other States cap it at a few "
            "thousand rupees. Ask before paying the full ad valorem rate, "
            "because the difference is large.",
            "A gift deed must be registered to transfer title at all. An "
            "unregistered gift of immovable property passes nothing, whatever "
            "the parties intended.",
        ),
    )
    result.instrument = "Gift deed"
    return result


def _mortgage(value: float, circle_rate: float, state: str | None, buyer: str) -> StampDutyResult:
    result = _conveyance(
        value, circle_rate, state, buyer, "Mortgage deed",
        multiplier=0.5,
        extra_notes=(
            "A mortgage with possession is generally charged at the full "
            "conveyance rate; a simple mortgage, without possession, at a "
            "fraction of it. This estimate assumes a simple mortgage.",
            "Most States cap duty on a mortgage securing a loan — the cap is "
            "commonly a few lakh rupees — so on a large facility the figure "
            "above will overstate what is payable.",
        ),
    )
    result.instrument = "Mortgage deed"
    result.concession = ""
    return result


def _lease(value: float, circle_rate: float, state: str | None, buyer: str) -> StampDutyResult:
    """
    Lease duty runs on the term, not the property's capital value.

    `value` here is the average annual rent, which is what the caller's form
    collects for this instrument.
    """
    key = (state or "").lower().replace(" ", "_")
    rule = STATE_RULES.get(key)
    authority = rule.authority if rule else "State Stamp Act"

    # Representative: leases under a year attract a small percentage of the
    # annual rent; the rate steps up with the term.
    annual = max(value, 0.0)
    duty = annual * 0.02
    registration = min(annual * 0.01, 30_000)

    return StampDutyResult(
        instrument="Lease or rent agreement",
        duty=f"approximately {_rupees(duty)}",
        registration_fee=f"approximately {_rupees(registration)}",
        total=f"approximately {_rupees(duty + registration)}",
        exact=False,
        charged_on=f"{_rupees(annual)} of annual rent",
        basis="A percentage of the average annual rent, stepping up with the term.",
        authority=authority,
        notes=[
            "Duty on a lease depends on its term. Up to five years attracts a "
            "small percentage of the annual rent; ten, twenty and ninety-nine "
            "year leases are charged progressively closer to the conveyance "
            "rate. This estimate assumes a short term.",
            "Any interest-free deposit is added to the rent for the purpose of "
            "computing duty in several States, so a large deposit raises the "
            "duty even though no rent changed hands.",
            "A lease of twelve months or more must be registered under Section "
            "17 of the Registration Act, 1908. This is why so many agreements "
            "are written for eleven months — an unregistered lease of a year "
            "or more is inadmissible to prove the tenancy's terms.",
        ],
        additional=[
            "Sub-registrar's charges, a few hundred rupees.",
            "Where an agent draws up the agreement, their fee is separate.",
        ],
    )


# ── Fixed-duty instruments ──────────────────────────────────────────────
def _fixed(
    label: str, amount: str, basis: str, authority: str,
    notes: tuple[str, ...] = (), additional: tuple[str, ...] = (),
) -> StampDutyResult:
    return StampDutyResult(
        instrument=label,
        duty=amount,
        registration_fee="Not applicable",
        total=amount,
        exact=True,
        charged_on="Not applicable — a fixed duty",
        basis=basis,
        authority=authority,
        notes=list(notes),
        additional=list(additional),
    )


def _affidavit(*_: object) -> StampDutyResult:
    return _fixed(
        "Affidavit",
        "₹10 to ₹100",
        "A fixed duty, set by each State.",
        "Indian Stamp Act, 1899 — Schedule I, Article 4, as amended by the States",
        notes=(
            "Buy the stamp paper in the deponent's own name — not the "
            "advocate's, and not someone else's. An affidavit on stamp paper "
            "issued to a third party is routinely objected to.",
            "Notarisation is a separate charge, commonly ₹50 to ₹200.",
        ),
    )


def _power_of_attorney(*_: object) -> StampDutyResult:
    return _fixed(
        "Power of attorney",
        "₹100 to ₹500, or ad valorem where it concerns property",
        "Fixed for an ordinary authority; charged as a conveyance where it "
        "gives the holder power to sell immovable property for consideration.",
        "Indian Stamp Act, 1899 — Schedule I, Article 48",
        notes=(
            "A general power of attorney given for consideration, or to a "
            "person who is not a close relative, and which authorises a sale, "
            "is charged as though it were a conveyance in most States — the "
            "full ad valorem rate, not ₹100.",
            "Suraj Lamp & Industries v. State of Haryana (2011) settled that a "
            "sale by power of attorney does not transfer title. A GPA sale "
            "buys litigation, not ownership.",
        ),
    )


def _will(*_: object) -> StampDutyResult:
    return _fixed(
        "Will",
        "No stamp duty",
        "A will attracts no stamp duty anywhere in India.",
        "Indian Succession Act, 1925",
        notes=(
            "Registration is optional under Section 18 of the Registration "
            "Act, 1908, and where a will is registered the fee is nominal — "
            "commonly ₹100 to ₹200.",
            "An unregistered will is perfectly valid. What it needs is two "
            "attesting witnesses, neither of whom should be a beneficiary.",
        ),
    )


def _partnership(*_: object) -> StampDutyResult:
    return _fixed(
        "Partnership deed",
        "₹500 to ₹5,000",
        "A fixed duty in most States; a few charge on the capital contributed.",
        "Indian Stamp Act, 1899 — Schedule I, Article 46, as amended by the States",
        notes=(
            "Registration of the firm under the Partnership Act, 1932 is "
            "separate from stamping and is not compulsory — but an "
            "unregistered firm cannot sue to enforce a contract under Section "
            "69, which is a serious disability to accept casually.",
        ),
    )


_AD_VALOREM = {
    "sale_deed": lambda v, c, s, b: _conveyance(v, c, s, b, "Sale deed / conveyance"),
    "gift_deed": _gift,
    "mortgage": _mortgage,
    "lease": _lease,
}

_FIXED = {
    "affidavit": _affidavit,
    "power_of_attorney": _power_of_attorney,
    "will": _will,
    "partnership": _partnership,
}

INSTRUMENTS = [
    {
        "id": "sale_deed",
        "label": "Sale deed / conveyance of property",
        "needs_value": True,
        "needs_state": True,
        "needs_buyer": True,
        "value_label": "Price agreed in the deed (₹)",
    },
    {
        "id": "gift_deed",
        "label": "Gift deed",
        "needs_value": True,
        "needs_state": True,
        "needs_buyer": True,
        "value_label": "Market value of the property (₹)",
    },
    {
        "id": "lease",
        "label": "Lease or rent agreement",
        "needs_value": True,
        "needs_state": True,
        "needs_buyer": False,
        "value_label": "Annual rent (₹)",
    },
    {
        "id": "mortgage",
        "label": "Mortgage deed",
        "needs_value": True,
        "needs_state": True,
        "needs_buyer": False,
        "value_label": "Amount secured (₹)",
    },
    {
        "id": "affidavit",
        "label": "Affidavit",
        "needs_value": False,
        "needs_state": False,
        "needs_buyer": False,
        "value_label": "",
    },
    {
        "id": "power_of_attorney",
        "label": "Power of attorney",
        "needs_value": False,
        "needs_state": False,
        "needs_buyer": False,
        "value_label": "",
    },
    {
        "id": "partnership",
        "label": "Partnership deed",
        "needs_value": False,
        "needs_state": False,
        "needs_buyer": False,
        "value_label": "",
    },
    {
        "id": "will",
        "label": "Will",
        "needs_value": False,
        "needs_state": False,
        "needs_buyer": False,
        "value_label": "",
    },
]

BUYERS = [
    {"id": "man", "label": "A man, solely"},
    {"id": "woman", "label": "A woman, solely"},
    {"id": "joint", "label": "Jointly, including a woman"},
]


def calculate(
    instrument: str,
    value: float = 0.0,
    circle_rate: float = 0.0,
    state: str | None = None,
    buyer: str = "man",
) -> StampDutyResult:
    if instrument in _FIXED:
        return _FIXED[instrument]()
    calculator = _AD_VALOREM.get(instrument)
    if calculator is None:
        raise KeyError(f"Unknown instrument: {instrument}")
    return calculator(max(value, 0.0), max(circle_rate, 0.0), state, buyer)


def catalogue() -> dict:
    return {"instruments": INSTRUMENTS, "states": STATES, "buyers": BUYERS}
