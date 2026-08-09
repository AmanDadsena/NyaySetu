"""
On-disk corpus store.

The hand-written passages in `corpus.py` are the editorial layer: plain-language
explanations of the provisions people actually ask about. They do not scale —
nobody is going to hand-write the whole of the Bharatiya Nyaya Sanhita into a
Python list.

This module holds the bulk layer: passages ingested from public sources, stored
as JSONL under `data/corpus/`. One file per source, one passage per line, so a
re-ingest replaces exactly one file and the diff is readable.

Both layers are merged at load time. When an ingested passage collides with a
hand-written one, the hand-written version wins: it was reviewed by a person.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from .corpus import Passage

#: backend/data/corpus/
STORE_DIR = Path(__file__).resolve().parents[2] / "data" / "corpus"

#: Fields that are tuples on the dataclass but arrays in JSON.
_TUPLE_FIELDS = ("topics", "also_known_as")


def _to_json(passage: Passage) -> dict:
    data = asdict(passage)
    for field in _TUPLE_FIELDS:
        data[field] = list(data[field])
    return data


def _from_json(data: dict) -> Passage:
    return Passage(
        id=data["id"],
        title=data["title"],
        act=data["act"],
        section=data.get("section", ""),
        text=data["text"],
        source_url=data.get("source_url", ""),
        topics=tuple(data.get("topics", ())),
        also_known_as=tuple(data.get("also_known_as", ())),
    )


def write(name: str, passages: list[Passage]) -> Path:
    """
    Write one source's passages to `data/corpus/<name>.jsonl`, replacing it.

    Replacing rather than appending is deliberate: re-running an ingest should
    be idempotent, and an append-only store slowly fills with superseded copies
    of the same section after an amendment.
    """
    STORE_DIR.mkdir(parents=True, exist_ok=True)
    path = STORE_DIR / f"{name}.jsonl"

    with path.open("w", encoding="utf-8") as handle:
        for passage in passages:
            handle.write(json.dumps(_to_json(passage), ensure_ascii=False) + "\n")

    return path


def load_all() -> list[Passage]:
    """Read every JSONL file in the store. Missing directory is not an error."""
    if not STORE_DIR.is_dir():
        return []

    passages: list[Passage] = []
    for path in sorted(STORE_DIR.glob("*.jsonl")):
        try:
            with path.open(encoding="utf-8") as handle:
                for line_number, line in enumerate(handle, 1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        passages.append(_from_json(json.loads(line)))
                    except (json.JSONDecodeError, KeyError) as exc:
                        # One bad line should not take down the whole index.
                        print(f"[store] skipping {path.name}:{line_number} ({exc})")
        except OSError as exc:
            print(f"[store] could not read {path.name}: {exc}")

    return passages


def stats() -> dict[str, int]:
    """Passage count per source file, for the health endpoint."""
    if not STORE_DIR.is_dir():
        return {}
    return {
        path.stem: sum(1 for line in path.open(encoding="utf-8") if line.strip())
        for path in sorted(STORE_DIR.glob("*.jsonl"))
    }
