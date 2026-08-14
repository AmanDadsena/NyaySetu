"""
Learning where the corpus is thin from what people ask.

The eval measures retrieval against questions we thought of. Users ask the ones
we did not, and when retrieval misses they rarely complain — they rephrase and
try again. That second attempt is the signal: someone who asks, reads, and
immediately rewords almost always did not get what they came for. Nobody has to
label anything.

**This is off unless switched on.** These are people's legal problems — a
question about a violent spouse or a bounced cheque is among the most sensitive
things a person will type. So logging requires `NYAYSETU_FEEDBACK_LOG` to be set
to a path, nothing is written anywhere else, and:

  * No user id, IP, account or session token is stored. The session key exists
    only to link consecutive questions and is a random client-side value that
    maps to nothing.
  * Question text is stored only when `NYAYSETU_FEEDBACK_TEXT=1`. Without it
    you still get the retrieval outcome and the rephrase signal, which is
    enough to see *that* a topic fails, just not the exact words.
  * The file is append-only JSONL, local to the deployment, and safe to delete.

Run `python -m scripts.gaps` to turn it into a ranked list of corpus gaps.
"""

from __future__ import annotations

import json
import os
import re
import threading
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

#: Where to append. Unset means the whole module does nothing.
LOG_PATH = os.environ.get("NYAYSETU_FEEDBACK_LOG", "")

#: Whether the question text itself may be stored. Off by default.
STORE_TEXT = os.environ.get("NYAYSETU_FEEDBACK_TEXT") == "1"

#: A second question inside this window counts as a retry of the first. Long
#: enough to read a short answer and decide it missed; short enough that a
#: genuinely new question is not swept up.
REPHRASE_WINDOW_SECONDS = float(os.environ.get("NYAYSETU_REPHRASE_WINDOW", "90"))

#: Word overlap above which two consecutive questions are the same question
#: asked differently, rather than a new one. Below it, the user moved on.
#:
#: Jaccard over short questions is harsh: "how do I get my security deposit
#: back" and "landlord kept my security deposit what to do" are plainly the same
#: question and score 0.33, because the stopwords each one happens to use count
#: against them. 0.30 catches that pair while still separating a drunk-driving
#: question from an RTI one, which share nothing.
REPHRASE_OVERLAP = float(os.environ.get("NYAYSETU_REPHRASE_OVERLAP", "0.30"))

_lock = threading.Lock()
_TOKEN_RE = re.compile(r"[\wऀ-෿]+", re.UNICODE)

#: session key -> (timestamp, tokens, entry index in this process)
_recent: dict[str, tuple[float, frozenset[str], dict]] = {}


@dataclass
class QueryRecord:
    at: float
    #: Passage ids returned, best first. Empty means the guards refused.
    retrieved: list[str] = field(default_factory=list)
    #: Score of the top hit, 0 when nothing came back.
    top_score: float = 0.0
    grounding: str = "none"
    language: str = "English"
    #: Set on the *earlier* record once a rephrase is seen after it.
    rephrased: bool = False
    #: Only present when NYAYSETU_FEEDBACK_TEXT=1.
    question: str | None = None


def enabled() -> bool:
    return bool(LOG_PATH)


def _tokens(text: str) -> frozenset[str]:
    return frozenset(m.group(0).lower() for m in _TOKEN_RE.finditer(text))


def _overlap(a: frozenset[str], b: frozenset[str]) -> float:
    """Jaccard overlap. Symmetric, so neither ordering is privileged."""
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _append(record: QueryRecord) -> None:
    try:
        path = Path(LOG_PATH)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")
    except OSError as exc:
        # Telemetry must never take the answer down with it.
        print(f"[feedback] could not write {LOG_PATH}: {exc}")


def record(
    question: str,
    retrieved: list[str],
    top_score: float,
    grounding: str,
    language: str = "English",
    session: str | None = None,
) -> None:
    """
    Note one question and what retrieval did with it.

    When the previous question from the same session was recent and shares
    enough vocabulary, that earlier question is marked as rephrased — the
    closest thing to a user saying "that was not what I meant".
    """
    if not enabled():
        return

    now = time.time()
    entry = QueryRecord(
        at=now,
        retrieved=list(retrieved),
        top_score=round(top_score, 4),
        grounding=grounding,
        language=language,
        question=question if STORE_TEXT else None,
    )

    with _lock:
        previous = _recent.get(session) if session else None
        if previous:
            when, tokens, earlier = previous
            if (
                now - when <= REPHRASE_WINDOW_SECONDS
                and _overlap(tokens, _tokens(question)) >= REPHRASE_OVERLAP
            ):
                # Rewrite the earlier record rather than the current one: it is
                # the question that failed, and the one worth a corpus passage.
                earlier["rephrased"] = True
                _append(QueryRecord(**earlier))
                _recent.pop(session, None)
                _append(entry)
                return

            # Previous question stood on its own; commit it unmarked.
            _append(QueryRecord(**earlier))

        if session:
            _recent[session] = (now, _tokens(question), asdict(entry))
            # Bound the map so a long-running process cannot grow without limit.
            if len(_recent) > 2000:
                oldest = sorted(_recent.items(), key=lambda kv: kv[1][0])[:500]
                for key, _ in oldest:
                    _, _, stale = _recent.pop(key)
                    _append(QueryRecord(**stale))
        else:
            _append(entry)


def flush_stale(older_than: float | None = None) -> int:
    """
    Write out held records that can no longer be rephrased.

    A record is held briefly so a follow-up can mark it. One that ages past the
    window never will, and holding it forever would lose it on restart.
    """
    if not enabled():
        return 0
    # Explicit None check: `older_than or WINDOW` would silently turn a
    # deliberate 0 — flush everything — into the default window.
    window = REPHRASE_WINDOW_SECONDS if older_than is None else older_than
    cutoff = time.time() - window
    written = 0
    with _lock:
        for key in [k for k, v in _recent.items() if v[0] < cutoff]:
            _, _, entry = _recent.pop(key)
            _append(QueryRecord(**entry))
            written += 1
    return written
