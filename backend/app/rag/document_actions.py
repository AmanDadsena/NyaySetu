"""
Turn a analysed document into things the reader can actually do.

The analyser was already good at describing a document and bad at being any use
afterwards. It would correctly identify a cheque bounce demand notice, list the
dates in it, and stop — leaving the one fact that matters unsaid, which is that
the recipient has fifteen days and the clock started when the notice was
served.

So each recognised document type is mapped to the toolkit entry that answers
"what now": a deadline to compute, a plan to follow, a letter to send. The links
are ordinary toolkit URLs with the selection pre-made, so the user lands on a
filled-in form rather than a menu.

Nothing here guesses at a date it cannot parse. An action carries a date only
when one was extracted unambiguously; otherwise the toolkit opens with the rule
chosen and the date blank, which is still most of the work done.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date

#: Signals that pin a document to a more specific type than the coarse
#: `document_type` label. A "Legal Notice" under Section 138 has a hard 15-day
#: consequence that a general legal notice does not, and telling them apart is
#: the difference between a useful suggestion and a generic one.
_REFINEMENTS: list[tuple[str, tuple[str, ...]]] = [
    ("Cheque Bounce Notice", (
        "section 138", "sec. 138", "s.138", "negotiable instruments",
        "dishonour", "dishonor", "insufficient funds", "cheque return memo",
    )),
    ("Consumer Notice", (
        "consumer protection act", "deficiency in service", "unfair trade practice",
    )),
    ("RTI Reply", (
        "right to information", "public information officer", "section 6(1)",
        "first appellate authority",
    )),
    ("Eviction / Rent Notice", (
        "quit and vacate", "vacate the premises", "eviction", "arrears of rent",
    )),
    ("Termination Letter", (
        "terminate your employment", "termination of employment", "last working day",
        "relieving", "notice period",
    )),
]

_MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11,
    "december": 12,
}

_DMY = re.compile(r"^(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})$")
_D_MONTH_Y = re.compile(
    r"^(\d{1,2})(?:st|nd|rd|th)?\s+([A-Za-z]+)\s+(\d{4})$", re.IGNORECASE
)
_MONTH_D_Y = re.compile(r"^([A-Za-z]+)\s+(\d{1,2}),?\s+(\d{4})$", re.IGNORECASE)


def parse_date(raw: str) -> date | None:
    """
    Parse one extracted date string, or give up.

    Day-first, because Indian legal documents are written that way and a
    misread date here would put a filing deadline in the wrong place. Anything
    ambiguous enough to need a guess returns None instead.
    """
    text = raw.strip()

    match = _DMY.match(text)
    if match:
        day, month, year = (int(g) for g in match.groups())
        if year < 100:
            year += 2000 if year < 70 else 1900
        # A value above 12 in the second position can only be a day, which
        # means the document is month-first and this is not safe to read.
        if month > 12:
            return None
        try:
            return date(year, month, day)
        except ValueError:
            return None

    match = _D_MONTH_Y.match(text)
    if match:
        day, month_name, year = match.group(1), match.group(2).lower(), match.group(3)
        if month_name in _MONTHS:
            try:
                return date(int(year), _MONTHS[month_name], int(day))
            except ValueError:
                return None

    match = _MONTH_D_Y.match(text)
    if match:
        month_name, day, year = match.group(1).lower(), match.group(2), match.group(3)
        if month_name in _MONTHS:
            try:
                return date(int(year), _MONTHS[month_name], int(day))
            except ValueError:
                return None

    return None


def most_recent_date(key_dates: list[str], today: date | None = None) -> date | None:
    """
    The date a deadline most likely runs from.

    Documents carry several dates — the agreement, the incident, the notice.
    The latest one that is not in the future is the best available proxy for
    "when this document was issued", which is what the periods key off.
    """
    today = today or date.today()
    parsed = [d for d in (parse_date(x) for x in key_dates) if d and d <= today]
    return max(parsed) if parsed else None


@dataclass
class Action:
    """One thing to do, and the toolkit URL that does it."""

    kind: str  # deadline | plan | draft
    label: str
    detail: str
    href: str
    #: True when a date was found and pre-filled, so the UI can say so.
    prefilled: bool = False


@dataclass
class ActionSet:
    refined_type: str
    actions: list[Action] = field(default_factory=list)


#: document type -> (limitation rule, plan situation, template, why it matters)
_ROUTES: dict[str, tuple[str | None, str | None, str | None, str]] = {
    "Cheque Bounce Notice": (
        "cheque_complaint", "cheque_bounced", "cheque_notice",
        "The drawer has 15 days from service to pay. If they do not, the "
        "complaint must be filed within the 30 days that follow.",
    ),
    "Consumer Notice": (
        "consumer_complaint", "defective_purchase", "consumer_notice",
        "A consumer complaint runs two years from the cause of action.",
    ),
    "RTI Reply": (
        "rti_first_appeal", "rti_ignored", "rti_first_appeal",
        "A first appeal must be filed within 30 days of this reply.",
    ),
    "Eviction / Rent Notice": (
        "suit_immovable_possession", "deposit_withheld", "legal_notice",
        "Check the notice period the agreement requires before acting on it.",
    ),
    "Termination Letter": (
        "wages_claim", "salary_unpaid", "legal_notice",
        "Dues on termination — salary, notice pay, gratuity — have their own "
        "time limits.",
    ),
    "Legal Notice": (
        None, None, "legal_notice",
        "A notice usually sets its own deadline to comply. Diary it.",
    ),
    "First Information Report": (
        None, "fir_refused", "fir_escalation",
        "If the police are not acting on it, there is a ladder above the station.",
    ),
    "Rent / Lease Agreement": (
        None, "deposit_withheld", None,
        "The deposit and notice terms here are what a later dispute turns on.",
    ),
    "Employment Agreement": (
        None, "salary_unpaid", None,
        "Notice period and non-compete clauses are the ones that bite later.",
    ),
    "Court Judgment / Order": (
        "appeal_district", None, None,
        "An appeal from a decree runs 30 days for a District Court, 90 for a High Court.",
    ),
}


def suggest(document_type: str, text: str, key_dates: list[str]) -> ActionSet:
    """Map an analysed document to concrete toolkit actions."""
    lowered = text.lower()

    refined = document_type
    best_score = 0
    for label, markers in _REFINEMENTS:
        score = sum(1 for m in markers if m in lowered)
        if score > best_score:
            refined, best_score = label, score

    route = _ROUTES.get(refined) or _ROUTES.get(document_type)
    if route is None:
        return ActionSet(refined_type=refined)

    rule_id, situation_id, template_id, detail = route
    anchor = most_recent_date(key_dates)
    on = f"&on={anchor.isoformat()}" if anchor else ""

    actions: list[Action] = []
    if situation_id:
        actions.append(
            Action(
                kind="plan",
                label="Build the full plan",
                detail=detail,
                href=f"/toolkit?t=plan&situation={situation_id}{on}",
                prefilled=anchor is not None,
            )
        )
    if rule_id:
        actions.append(
            Action(
                kind="deadline",
                label="Work out the deadline",
                detail=(
                    f"Counted from {anchor.isoformat()}, the latest date found in this "
                    "document. Change it if the clock starts elsewhere."
                    if anchor
                    else "Enter the date the clock starts and this will compute it."
                ),
                href=f"/toolkit?t=deadline&rule={rule_id}{on}",
                prefilled=anchor is not None,
            )
        )
    if template_id:
        actions.append(
            Action(
                kind="draft",
                label="Draft the reply",
                detail="Opens the matching template with the right headings already in place.",
                href=f"/toolkit?t=draft&template={template_id}",
            )
        )

    return ActionSet(refined_type=refined, actions=actions)
