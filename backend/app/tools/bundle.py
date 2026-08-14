"""
The toolkit's lookup tables, as data.

The deadline calculator needs three things: a table of limitation periods,
calendar arithmetic, and a list of days the court is shut. None of it is a
secret and none of it needs a server — but shipping it as an API meant that a
person on a train, or on the kind of connection this app is actually for, got
nothing at all from a tool that is pure arithmetic.

So the tables are served once, cached in the browser, and the arithmetic is
repeated client-side. That duplication is the obvious risk, and it is answered
by `scripts/check_offline_parity.py`, which runs every rule through both
implementations and fails if they ever disagree.

Only data goes over the wire. The client re-derives everything else, so a rule
corrected here reaches every cached client on their next online visit without
a deploy.
"""

from __future__ import annotations

from datetime import date

from app.tools import fees, forum, holidays, limitation

#: Bumped whenever the *shape* of the payload changes, so a browser holding an
#: older cache discards it instead of reading fields that have moved. Content
#: changes do not need a bump; `generated` covers those.
SCHEMA_VERSION = 1


def build() -> dict:
    """Everything the browser needs to answer without us."""
    return {
        "schema": SCHEMA_VERSION,
        "generated": date.today().isoformat(),
        "limitation": [
            {
                "id": rule.id,
                "label": rule.label,
                "category": rule.category,
                "trigger": rule.trigger,
                "citation": (
                    f"{rule.act} — {rule.section}" if rule.section != "—" else rule.act
                ),
                # The period itself, as the three components the arithmetic
                # needs. All null means the law sets no limit at all.
                "years": rule.years,
                "months": rule.months,
                "days": rule.days,
                "condonable": rule.condonable,
                "condonation_note": rule.condonation_note,
                "notes": list(rule.notes),
                "related": list(rule.related),
            }
            for rule in limitation.RULES
        ],
        "forum": forum.catalogue(),
        "fees": fees.catalogue(),
        "holidays": {
            # Keyed "MM-DD" so the client does not have to parse a tuple.
            "fixed": {
                f"{month:02d}-{day:02d}": name
                for (month, day), name in holidays.FIXED_HOLIDAYS.items()
            },
            # Notified court calendars for the years a user could plausibly be
            # computing against. Empty where the deployment has none.
            "notified": {
                str(year): sorted(d.isoformat() for d in holidays._notified(year))
                for year in range(date.today().year - 1, date.today().year + 3)
            },
        },
    }
