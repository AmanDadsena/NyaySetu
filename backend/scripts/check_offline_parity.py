"""
Prove the browser and the server compute the same deadline.

`frontend/src/lib/toolkit/offline.ts` re-implements `app/tools/limitation.py`
so the toolkit keeps working with no network. Duplicated logic drifts, and here
drift means telling somebody the wrong last day to file. So rather than trust
that the two stay aligned, run every rule through both across a spread of dates
chosen to hit the cases that actually differ between implementations — leap
days, month ends, deadlines landing on weekends and gazetted holidays.

    python -m scripts.check_offline_parity

Exits non-zero on any disagreement, so it belongs next to the eval in CI.
Requires `node` on PATH; skips with a clear message if it is missing.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.tools import bundle, limitation  # noqa: E402

OFFLINE_TS = (
    Path(__file__).resolve().parents[2]
    / "frontend" / "src" / "lib" / "toolkit" / "offline.ts"
)

#: Dates picked to break naive arithmetic rather than to be representative.
EVENT_DATES = [
    "2024-02-29",  # leap day: +3 years must clamp to 28 Feb
    "2024-01-31",  # month end: +1 month must clamp, not spill
    "2023-12-31",  # year boundary
    "2025-01-26",  # deadline may land on Republic Day
    "2025-08-15",  # Independence Day
    "2025-03-15",  # ordinary mid-month control
    "2022-05-01",  # May Day, and long enough ago to be expired
    "2025-12-25",  # Christmas
]

#: Fields both implementations must agree on exactly. `notes` is excluded: the
#: server localises and reorders them, and they carry no date.
COMPARED = [
    "rule_id", "has_limitation", "deadline", "days_remaining", "expired",
    "days_overdue", "urgency", "filing_date", "filing_date_confidence",
    "filing_reasons", "condonable",
]

# Today is pinned so the run is reproducible and does not fail overnight.
TODAY = "2026-08-14"

JS_HARNESS = """
const {{ calculateLocally }} = require({module});
const bundle = require({bundlefile});
const cases = require({casefile});
const out = cases.map(([ruleId, eventDate]) => {{
  try {{
    return calculateLocally(bundle, ruleId, eventDate, {today!r});
  }} catch (e) {{
    return {{ error: String(e), rule_id: ruleId }};
  }}
}});
process.stdout.write(JSON.stringify(out));
"""


def _strip_types(source: str) -> str:
    """
    Run the TypeScript through esbuild so `node` can require it.

    Written as a shell-out rather than a hand-rolled type stripper because a
    parity check that tests a mangled copy of the file proves nothing.
    """
    result = subprocess.run(
        ["npx", "--yes", "esbuild", "--loader=ts", "--format=cjs", "--platform=node"],
        input=source.encode(),
        capture_output=True,
        shell=(sys.platform == "win32"),
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode()[:800])
    return result.stdout.decode()


def main() -> int:
    if shutil.which("node") is None:
        print("node not found on PATH — skipping parity check.")
        return 0
    if not OFFLINE_TS.is_file():
        print(f"Client implementation not found at {OFFLINE_TS}")
        return 1

    cases = [
        (rule.id, event)
        for rule in limitation.RULES
        for event in EVENT_DATES
    ]
    today = date.fromisoformat(TODAY)

    expected = []
    for rule_id, event in cases:
        result = limitation.calculate(rule_id, date.fromisoformat(event), today=today)
        expected.append({k: getattr(result, k) for k in COMPARED})

    payload = bundle.build()

    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        # esbuild strips the types; `process.env` is referenced at module load.
        compiled = _strip_types(OFFLINE_TS.read_text(encoding="utf-8"))
        (tmpdir / "offline.js").write_text(compiled, encoding="utf-8")
        (tmpdir / "bundle.json").write_text(json.dumps(payload), encoding="utf-8")
        (tmpdir / "cases.json").write_text(json.dumps(cases), encoding="utf-8")
        (tmpdir / "run.js").write_text(
            JS_HARNESS.format(
                module=json.dumps(str(tmpdir / "offline.js")),
                bundlefile=json.dumps(str(tmpdir / "bundle.json")),
                casefile=json.dumps(str(tmpdir / "cases.json")),
                today=TODAY,
            ),
            encoding="utf-8",
        )

        run = subprocess.run(
            ["node", str(tmpdir / "run.js")],
            capture_output=True,
            shell=(sys.platform == "win32"),
        )
        if run.returncode != 0:
            print("Client harness failed:")
            print(run.stderr.decode()[:1500])
            return 1
        actual = json.loads(run.stdout.decode())

    mismatches = []
    for (rule_id, event), want, got in zip(cases, expected, actual):
        if "error" in got:
            mismatches.append((rule_id, event, "error", got["error"], ""))
            continue
        for field in COMPARED:
            a, b = want[field], got.get(field)
            if a != b:
                mismatches.append((rule_id, event, field, a, b))

    print(
        f"\nOffline parity: {len(limitation.RULES)} rules x {len(EVENT_DATES)} dates "
        f"= {len(cases)} cases, comparing {len(COMPARED)} fields each\n"
    )
    if mismatches:
        print(f"  {len(mismatches)} DISAGREEMENTS:\n")
        for rule_id, event, field, server, client in mismatches[:40]:
            print(f"    {rule_id} @ {event}  {field}")
            print(f"      server={server!r}")
            print(f"      client={client!r}")
        if len(mismatches) > 40:
            print(f"    … and {len(mismatches) - 40} more")
        return 1

    print("  Server and browser agree on every case.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
