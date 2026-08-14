"""
Maintenance estimator.

There is no statutory formula for maintenance in India. None of Section 125
CrPC (now Section 144 BNSS), Section 24 of the Hindu Marriage Act, Section 18
of the Hindu Adoptions and Maintenance Act or Section 20 of the Domestic
Violence Act prescribes a percentage, a multiplier, or a table. The amount is
discretionary, decided case by case on the criteria the Supreme Court set out
in *Rajnesh v. Neha* (2021) 2 SCC 324.

That makes this tool different from every other one in the toolkit, and it is
built differently on purpose:

  * **It returns a range, never a figure.** A single number would be read as
    an entitlement. It is not one, and a person who walks into a Family Court
    expecting the number this software gave them has been misled by it.

  * **Every band is anchored to a reported decision**, named and citable, so
    the user can see where the percentage comes from and a lawyer can check it.
    The most-cited anchor is *Kalyan Dey Chowdhury v. Rita Dey Chowdhury*
    (2017) 14 SCC 200, where 25% of the husband's net salary was held to be
    "just and proper" for a wife. It is a benchmark drawn from one case, not a
    rule of general application, and it is labelled that way.

  * **The factors that move the figure are listed beside it**, because in
    practice they matter more than the arithmetic. Standard of living during
    the marriage, the wife's qualifications, the husband's liabilities, and
    who the children live with will each move an award further than the
    difference between 20% and 30%.

What the tool can be precise about is procedure — which provision to file
under, that the *Rajnesh* affidavit of disclosure is mandatory in every
maintenance case in the country, and that maintenance runs from the date of
the application, not the date of the order. Those are the parts people lose
money by not knowing.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Precedent:
    case: str
    citation: str
    proposition: str


@dataclass
class MaintenanceResult:
    #: Monthly range, formatted. Never a single figure.
    monthly_low: str
    monthly_high: str
    #: The same range as a share of the payer's net income.
    share_low: str
    share_high: str
    #: Who the range covers.
    covers: str
    basis: str
    #: Always False. There is no exact answer here and the UI should say so.
    exact: bool = False
    #: True where the dependants would together exceed the practical ceiling,
    #: so the headline range is lower than the breakdown sums to.
    capped: bool = False
    breakdown: list[dict] = field(default_factory=list)
    #: Things that will move the figure up or down, in plain words.
    raises: list[str] = field(default_factory=list)
    lowers: list[str] = field(default_factory=list)
    precedents: list[dict] = field(default_factory=list)
    #: Where to file and under what.
    provisions: list[dict] = field(default_factory=list)
    procedure: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


def _rupees(value: float) -> str:
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


# ── Bands, each tied to a source ────────────────────────────────────────
#: Wife or husband claiming as a spouse. The 25% anchor sits inside this band
#: rather than being reported as the answer.
SPOUSE_BAND = (0.20, 0.30)

#: Per child. Courts commonly award less per child than for a spouse, and more
#: where the child is older or in private education.
CHILD_BAND = (0.08, 0.13)

#: Parents claiming under Section 144 BNSS, where the obligation is shared
#: among the children.
PARENT_BAND = (0.05, 0.10)

#: Courts rarely leave a payer with less than half their net income. Awards
#: beyond this exist but are exceptional, and quoting one as a likely outcome
#: would be misleading.
CEILING = 0.50


PRECEDENTS = {
    "kalyan_dey": Precedent(
        case="Kalyan Dey Chowdhury v. Rita Dey Chowdhury Nee Nandy",
        citation="(2017) 14 SCC 200",
        proposition=(
            "25% of the husband's net salary was held to be just and proper as "
            "maintenance for the wife. This is the figure most often quoted, "
            "but it was a decision on those facts — not a statutory rate."
        ),
    ),
    "rajnesh": Precedent(
        case="Rajnesh v. Neha",
        citation="(2021) 2 SCC 324",
        proposition=(
            "Laid down the criteria for quantifying maintenance and made an "
            "Affidavit of Disclosure of Assets and Liabilities mandatory from "
            "both parties in every maintenance case in India. Also held that "
            "maintenance is payable from the date of the application, not the "
            "date of the order."
        ),
    ),
    "kulbhushan": Precedent(
        case="Dr. Kulbhushan Kumar v. Raj Kumari",
        citation="(1970) 3 SCC 129",
        proposition=(
            "25% of the husband's net income was described as a reasonable "
            "figure for the wife — the origin of the 25% benchmark that later "
            "decisions have followed."
        ),
    ),
    "shailja": Precedent(
        case="Shailja v. Khobbanna",
        citation="(2018) 12 SCC 199",
        proposition=(
            "A wife who is *capable* of earning is not on that account "
            "disentitled to maintenance. Capacity to earn and actually earning "
            "are different things."
        ),
    ),
    "chaturbhuj": Precedent(
        case="Chaturbhuj v. Sita Bai",
        citation="(2008) 2 SCC 316",
        proposition=(
            "The object of Section 125 is to prevent vagrancy and destitution. "
            "The provision is a measure of social justice and is construed in "
            "favour of the claimant."
        ),
    ),
    "anju_garg": Precedent(
        case="Anju Garg v. Deepak Kumar Garg",
        citation="(2022) SCC OnLine SC 1314",
        proposition=(
            "A husband who is able-bodied is obliged to maintain his wife and "
            "minor children, and cannot plead a lack of income where he has "
            "the capacity to earn."
        ),
    ),
    "rana_nahid": Precedent(
        case="Rana Nahid v. Sahidul Haq Chisti",
        citation="(2020) 7 SCC 657",
        proposition=(
            "A Muslim woman may claim under Section 125 CrPC; the Muslim "
            "Women (Protection of Rights on Divorce) Act, 1986 does not take "
            "that remedy away."
        ),
    ),
    "mohd_abdul": Precedent(
        case="Mohd. Abdul Samad v. State of Telangana",
        citation="(2024) SCC OnLine SC 1686",
        proposition=(
            "Confirmed that Section 125 CrPC applies to all married women "
            "irrespective of religion, and that a divorced Muslim woman may "
            "invoke it independently of the 1986 Act."
        ),
    ),
}


PROVISIONS = {
    "bnss": {
        "label": "Section 144, Bharatiya Nagarik Suraksha Sanhita, 2023",
        "was": "Section 125, Code of Criminal Procedure, 1973",
        "who": "Wife, minor children, and parents unable to maintain themselves.",
        "where": "Judicial Magistrate First Class.",
        "why": (
            "Fastest route, available regardless of religion, and no court fee "
            "worth speaking of. An order can be enforced by warrant, and "
            "arrears are recoverable."
        ),
    },
    "hma24": {
        "label": "Section 24, Hindu Marriage Act, 1955",
        "was": "",
        "who": "Either spouse, where a matrimonial proceeding is already pending.",
        "where": "The court hearing the matrimonial petition.",
        "why": (
            "Interim maintenance and litigation expenses while the main case "
            "runs. Gender-neutral on its face — a husband without means may "
            "claim from a wife who has them."
        ),
    },
    "hma25": {
        "label": "Section 25, Hindu Marriage Act, 1955",
        "was": "",
        "who": "Either spouse, at or after the decree.",
        "where": "The court that passed the decree.",
        "why": (
            "Permanent alimony. May be a monthly sum or a lump sum, and can be "
            "varied later if circumstances change."
        ),
    },
    "hama18": {
        "label": "Section 18, Hindu Adoptions and Maintenance Act, 1956",
        "was": "",
        "who": "A Hindu wife, from her husband, without any other proceeding pending.",
        "where": "Civil court.",
        "why": (
            "A standalone right to be maintained, including where she is "
            "living separately for cause — cruelty, desertion, or his keeping "
            "a concubine."
        ),
    },
    "dv20": {
        "label": "Section 20, Protection of Women from Domestic Violence Act, 2005",
        "was": "",
        "who": "An aggrieved woman in a domestic relationship.",
        "where": "Judicial Magistrate First Class.",
        "why": (
            "Monetary relief covering maintenance, loss of earnings, medical "
            "expenses and damage to property — and it can be claimed alongside "
            "a Section 144 BNSS application, not instead of it."
        ),
    },
    "sma36": {
        "label": "Sections 36 and 37, Special Marriage Act, 1954",
        "was": "",
        "who": "Parties to a civil marriage.",
        "where": "The court hearing the petition.",
        "why": "Interim and permanent maintenance for marriages under this Act.",
    },
}


def _band(
    payer_income: float,
    spouse: bool,
    children: int,
    parents: int,
) -> tuple[float, float, list[dict]]:
    """Build the range and show what each dependant contributes to it."""
    low = high = 0.0
    breakdown: list[dict] = []

    if spouse:
        lo, hi = SPOUSE_BAND
        low += lo
        high += hi
        breakdown.append({
            "for": "Spouse",
            "share": f"{lo * 100:.0f}–{hi * 100:.0f}% of net income",
            "amount": f"{_rupees(payer_income * lo)} – {_rupees(payer_income * hi)}",
            "anchor": "Kalyan Dey Chowdhury (2017) 14 SCC 200 — 25% held just and proper",
        })

    if children > 0:
        lo, hi = CHILD_BAND
        low += lo * children
        high += hi * children
        breakdown.append({
            "for": f"{children} child" + ("ren" if children > 1 else ""),
            "share": f"{lo * 100:.0f}–{hi * 100:.0f}% each",
            "amount": (
                f"{_rupees(payer_income * lo * children)} – "
                f"{_rupees(payer_income * hi * children)}"
            ),
            "anchor": (
                "School fees and medical costs are commonly ordered separately, "
                "over and above this"
            ),
        })

    if parents > 0:
        lo, hi = PARENT_BAND
        low += lo * parents
        high += hi * parents
        breakdown.append({
            "for": f"{parents} parent" + ("s" if parents > 1 else ""),
            "share": f"{lo * 100:.0f}–{hi * 100:.0f}% each",
            "amount": (
                f"{_rupees(payer_income * lo * parents)} – "
                f"{_rupees(payer_income * hi * parents)}"
            ),
            "anchor": "Section 144 BNSS — the obligation is shared among all the children",
        })

    return low, high, breakdown


def calculate(
    payer_income: float,
    claimant_income: float = 0.0,
    spouse: bool = True,
    children: int = 0,
    parents: int = 0,
) -> MaintenanceResult:
    """
    Produce a defensible range, not a number.

    `payer_income` and `claimant_income` are monthly and net — take-home after
    statutory deductions, which is what courts work from, not gross.
    """
    payer_income = max(payer_income, 0.0)
    claimant_income = max(claimant_income, 0.0)
    children = max(int(children), 0)
    parents = max(int(parents), 0)

    low, high, breakdown = _band(payer_income, spouse, children, parents)

    notes: list[str] = []
    capped = False
    if high > CEILING:
        capped = True
        # Scale the whole band down proportionately rather than clipping only
        # the top, so the range keeps its shape.
        scale = CEILING / high
        low *= scale
        high = CEILING

    monthly_low = payer_income * low
    monthly_high = payer_income * high

    lowers: list[str] = []
    raises: list[str] = []

    if claimant_income > 0:
        ratio = claimant_income / payer_income if payer_income else 0
        lowers.append(
            f"The claimant's own income of {_rupees(claimant_income)} a month "
            f"will be set off. Courts reduce rather than refuse: earning "
            f"something does not end the right to be maintained, and the "
            f"comparison the court makes is with the standard of living during "
            f"the marriage, not with subsistence."
        )
        if ratio >= 1:
            lowers.append(
                "Where the claimant earns as much as or more than the "
                "respondent, maintenance for the spouse is often refused "
                "altogether — though maintenance for the children is not."
            )
        # Reduce the band by roughly the claimant's share of the joint income,
        # which is how a court's reasoning tends to run in practice.
        offset = min(ratio, 1.0) * 0.5
        monthly_low *= 1 - offset
        monthly_high *= 1 - offset

    if capped:
        notes.append(
            "The dependants entered would, at the upper end, take more than "
            "half the respondent's net income. Courts rarely go beyond that — "
            "the payer has to be left able to subsist — so the range has been "
            "brought back to a realistic ceiling."
        )

    raises.extend([
        "A high standard of living during the marriage — the claimant is "
        "entitled to something approaching it, not merely to survive.",
        "The claimant having given up a career or education for the family.",
        "Undisclosed income on the respondent's side. Courts routinely infer "
        "income from lifestyle where the affidavit is not believed.",
        "A child with special needs, in private education, or in higher study.",
    ])
    lowers.extend([
        "Genuine liabilities of the respondent — a home loan on the house the "
        "claimant lives in, or maintenance already payable to someone else.",
        "The claimant's own assets producing income, such as rent.",
        "A short marriage with no children, where permanent alimony is "
        "concerned rather than interim maintenance.",
    ])

    covers_parts = []
    if spouse:
        covers_parts.append("spouse")
    if children:
        covers_parts.append(f"{children} child" + ("ren" if children > 1 else ""))
    if parents:
        covers_parts.append(f"{parents} parent" + ("s" if parents > 1 else ""))
    covers = ", ".join(covers_parts) if covers_parts else "no dependants selected"

    precedent_keys = ["rajnesh", "kalyan_dey", "kulbhushan", "chaturbhuj"]
    if claimant_income > 0:
        precedent_keys.insert(2, "shailja")
    if children:
        precedent_keys.append("anju_garg")

    return MaintenanceResult(
        monthly_low=_rupees(monthly_low),
        monthly_high=_rupees(monthly_high),
        share_low=f"{(monthly_low / payer_income * 100) if payer_income else 0:.0f}%",
        share_high=f"{(monthly_high / payer_income * 100) if payer_income else 0:.0f}%",
        covers=covers,
        basis=(
            "A range built from percentages actually awarded in reported cases, "
            "applied to the respondent's net monthly income. There is no "
            "statutory formula — the amount is discretionary."
        ),
        exact=False,
        capped=capped,
        breakdown=breakdown,
        raises=raises,
        lowers=lowers,
        precedents=[
            {
                "case": PRECEDENTS[k].case,
                "citation": PRECEDENTS[k].citation,
                "proposition": PRECEDENTS[k].proposition,
            }
            for k in precedent_keys
        ],
        provisions=[
            {"id": k, **v} for k, v in PROVISIONS.items()
        ],
        procedure=[
            "File the Affidavit of Disclosure of Assets and Liabilities. "
            "Rajnesh v. Neha made it mandatory for both sides in every "
            "maintenance case, and a court will not fix a figure without it.",
            "Ask for maintenance from the date of the application. Rajnesh "
            "settled that it runs from then, not from the date of the order — "
            "and proceedings take years, so this is usually the largest single "
            "sum in the case.",
            "Attach proof of the respondent's income if you have it: salary "
            "slips, Form 16, income tax returns, bank statements, or the "
            "registration papers of a vehicle. Where income is concealed, "
            "courts draw inferences from what is spent.",
            "Claim litigation expenses too. They are separately payable under "
            "Section 24 of the Hindu Marriage Act and are routinely ordered.",
            "Applications under Section 144 BNSS and Section 20 of the Domestic "
            "Violence Act can both be filed. Rajnesh requires you to disclose "
            "the other proceedings, and any sum already received is adjusted — "
            "but filing both is not an abuse.",
            "If an order is not obeyed, apply for recovery. The Magistrate can "
            "issue a warrant and, for persistent default, order imprisonment "
            "until payment.",
        ],
        notes=notes + [
            "This is a range of outcomes in comparable reported cases. It is "
            "not a prediction, and nobody is entitled to a figure because "
            "software produced it.",
            "Free legal aid is available to every woman claiming maintenance, "
            "regardless of income, under Section 12(c) of the Legal Services "
            "Authorities Act, 1987. Call 15100.",
        ],
    )


def catalogue() -> dict:
    """Static reference the UI can show before any figures are entered."""
    return {
        "precedents": [
            {"case": p.case, "citation": p.citation, "proposition": p.proposition}
            for p in PRECEDENTS.values()
        ],
        "provisions": [{"id": k, **v} for k, v in PROVISIONS.items()],
        "factors": [
            "Status of the parties and the standard of living in the "
            "matrimonial home.",
            "Reasonable needs of the claimant and the children.",
            "The claimant's qualifications, employment, and independent income "
            "or assets.",
            "Whether the claimant gave up employment for the family.",
            "The respondent's income, other maintenance obligations, and "
            "genuine liabilities.",
            "Reasonable litigation expenses of a non-earning spouse.",
        ],
        "factors_source": "Rajnesh v. Neha, (2021) 2 SCC 324",
    }
