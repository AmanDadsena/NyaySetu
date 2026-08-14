"""
Where the corpus is thin, according to the people using it.

Reads the feedback log written by `app/rag/feedback.py` and ranks what to fix.
Three signals, in descending order of how much they should worry you:

  * **Refused** — retrieval returned nothing. Either the corpus has no answer or
    the guards are too tight. Either way somebody left with nothing.
  * **Rephrased** — an answer came back and the user immediately asked again in
    different words. The strongest available evidence that a confident answer
    was the wrong one, and the reason this log exists.
  * **Weak** — answered, but barely above the relevance floor. These are the
    ones that will start failing as the corpus grows and the idf shifts.

    python -m scripts.gaps                  # default log path
    python -m scripts.gaps --log path.jsonl
    python -m scripts.gaps --min-count 3

Passages are named where the log has them, so a topic that keeps failing points
at the passage that keeps almost-matching — usually the one whose vocabulary
needs widening rather than a new passage entirely.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

#: Below this the answer was only just admitted; worth watching.
WEAK_SCORE = 0.35


def load(path: Path) -> list[dict]:
    if not path.is_file():
        print(f"No feedback log at {path}.")
        print("Set NYAYSETU_FEEDBACK_LOG to a path and restart the backend to collect one.")
        return []
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return records


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--log",
        default=os.environ.get("NYAYSETU_FEEDBACK_LOG", "data/feedback.jsonl"),
    )
    parser.add_argument("--min-count", type=int, default=1)
    parser.add_argument("--top", type=int, default=20)
    args = parser.parse_args()

    records = load(Path(args.log))
    if not records:
        return 0

    refused = [r for r in records if not r.get("retrieved")]
    rephrased = [r for r in records if r.get("rephrased")]
    weak = [
        r for r in records
        if r.get("retrieved") and 0 < r.get("top_score", 0) < WEAK_SCORE
    ]

    total = len(records)
    print(f"\n{total} questions logged\n")
    print(f"  refused (nothing returned)   {len(refused):>5}  {len(refused)/total:>6.1%}")
    print(f"  rephrased after an answer    {len(rephrased):>5}  {len(rephrased)/total:>6.1%}")
    print(f"  answered weakly              {len(weak):>5}  {len(weak)/total:>6.1%}")

    has_text = any(r.get("question") for r in records)
    if not has_text:
        print("\n  Question text was not stored (NYAYSETU_FEEDBACK_TEXT is unset), so")
        print("  the breakdown below is by passage and language only.")

    # Which passages keep being retrieved and then rejected by the user. These
    # are near-misses: the topic is in the corpus, the wording is not.
    near_miss = Counter()
    for r in rephrased:
        for pid in r.get("retrieved", [])[:1]:
            near_miss[pid] += 1

    if near_miss:
        print("\nPassages returned just before a rephrase — widen their vocabulary:\n")
        for pid, count in near_miss.most_common(args.top):
            if count < args.min_count:
                continue
            print(f"  {count:>4}x  {pid}")

    by_language = Counter(r.get("language", "?") for r in refused)
    if by_language:
        print("\nRefusals by language — a spike here is a lexicon gap, not a corpus gap:\n")
        for language, count in by_language.most_common():
            print(f"  {count:>4}x  {language}")

    if has_text:
        print("\nQuestions that returned nothing:\n")
        seen = Counter(
            r["question"].strip().lower() for r in refused if r.get("question")
        )
        for question, count in seen.most_common(args.top):
            if count < args.min_count:
                continue
            print(f"  {count:>4}x  {question[:88]}")

        print("\nQuestions the user immediately reworded:\n")
        seen = Counter(
            r["question"].strip().lower() for r in rephrased if r.get("question")
        )
        for question, count in seen.most_common(args.top):
            if count < args.min_count:
                continue
            print(f"  {count:>4}x  {question[:88]}")

    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
