"""
Court working days.

Section 4 of the Limitation Act, 1963 lets you file on the next day the court
is open when the prescribed period expires on a holiday. Until now the
calculator flagged that as a caveat, because court calendars are notified per
court and change every year.

This makes it exact where it safely can be. Gazetted holidays that are fixed by
the Gregorian calendar are hardcoded; the movable ones — most Hindu, Islamic
and Christian festivals — are not, because their dates shift and a wrong date
here would move a filing deadline. Those are handled by letting a deployment
supply the year's notified list.

The rule the code follows: never move a deadline *earlier*, and when unsure,
say so rather than guess. A deadline reported one day late is a lost case; a
deadline reported one day early costs nothing.
"""

from __future__ import annotations

import json
import os
from datetime import date, timedelta
from functools import lru_cache
from pathlib import Path

#: Where a deployment can drop its court's notified calendar.
#: Format: {"2026": ["2026-01-26", "2026-08-15", …]}
HOLIDAY_FILE = Path(
    os.environ.get(
        "NYAYSETU_HOLIDAY_FILE",
        str(Path(__file__).resolve().parents[2] / "data" / "court_holidays.json"),
    )
)

#: Holidays that fall on the same Gregorian date every year and are gazetted
#: nationally. Safe to hardcode; everything movable is not.
FIXED_HOLIDAYS: dict[tuple[int, int], str] = {
    (1, 26): "Republic Day",
    (5, 1): "May Day",
    (8, 15): "Independence Day",
    (10, 2): "Gandhi Jayanti",
    (12, 25): "Christmas Day",
}


@lru_cache(maxsize=8)
def _notified(year: int) -> frozenset[date]:
    """Load a court's notified holiday list for the year, if one is present."""
    if not HOLIDAY_FILE.is_file():
        return frozenset()
    try:
        data = json.loads(HOLIDAY_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        print(f"[holidays] could not read {HOLIDAY_FILE}: {exc}")
        return frozenset()

    entries = data.get(str(year), [])
    parsed: set[date] = set()
    for entry in entries:
        try:
            parsed.add(date.fromisoformat(entry))
        except (ValueError, TypeError):
            continue
    return frozenset(parsed)


def is_weekend(day: date) -> bool:
    """Saturday and Sunday. Some courts sit on alternate Saturdays; that
    variation is why the result is described as 'on or after' rather than
    presented as the only possible filing date."""
    return day.weekday() >= 5


def holiday_name(day: date) -> str | None:
    if day in _notified(day.year):
        return "Court holiday (notified)"
    return FIXED_HOLIDAYS.get((day.month, day.day))


def is_working_day(day: date) -> bool:
    return not is_weekend(day) and holiday_name(day) is None


def next_working_day(day: date, limit: int = 30) -> tuple[date, list[str]]:
    """
    Move forward to the next day the court is open.

    Returns the date and a human explanation of every day skipped, so the user
    can see *why* their deadline moved rather than being handed a different
    date with no account of it.
    """
    reasons: list[str] = []
    cursor = day

    for _ in range(limit):
        if is_working_day(cursor):
            return cursor, reasons
        if is_weekend(cursor):
            reasons.append(f"{cursor.isoformat()} is a {cursor.strftime('%A')}")
        else:
            reasons.append(f"{cursor.isoformat()} is {holiday_name(cursor)}")
        cursor += timedelta(days=1)

    # Something is wrong with the calendar data; do not silently loop.
    return day, ["Could not resolve a working day within 30 days — using the raw date."]


def resolve_filing_date(deadline: date) -> dict:
    """
    Apply Section 4 to a computed deadline.

    Never moves the date earlier. Where no notified calendar has been supplied,
    the result says so, because only weekends and the fixed national holidays
    were considered.
    """
    if is_working_day(deadline):
        return {
            "deadline": deadline.isoformat(),
            "filing_date": deadline.isoformat(),
            "moved": False,
            "reasons": [],
            "confidence": "high",
            "note": "",
        }

    filing, reasons = next_working_day(deadline)
    have_calendar = bool(_notified(deadline.year))

    return {
        "deadline": deadline.isoformat(),
        "filing_date": filing.isoformat(),
        "moved": filing != deadline,
        "reasons": reasons,
        "confidence": "high" if have_calendar else "partial",
        "note": (
            "Section 4 of the Limitation Act, 1963 allows filing on the next day "
            "the court is open."
            + (
                ""
                if have_calendar
                else " Only weekends and the fixed national holidays were checked — "
                "no notified court calendar is configured for this year, so a local "
                "vacation or festival could push this further. Confirm with the "
                "court before relying on the last day."
            )
        ),
    }


def calendar_status() -> dict:
    """What the deployment actually knows about, for the health endpoint."""
    this_year = date.today().year
    return {
        "file": str(HOLIDAY_FILE),
        "configured": HOLIDAY_FILE.is_file(),
        "notified_days_this_year": len(_notified(this_year)),
        "fixed_holidays": len(FIXED_HOLIDAYS),
    }
