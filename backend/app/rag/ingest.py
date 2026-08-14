"""
Ingest public legal sources into the corpus.

    python -m app.rag.ingest bare-act path/to/act.txt \
        --name bns_2023 \
        --act "Bharatiya Nyaya Sanhita, 2023" \
        --url https://www.indiacode.nic.in/...

    python -m app.rag.ingest refresh      # re-run every configured source
    python -m app.rag.ingest list         # what is currently in the store

**On sources.** Only material that is free to reproduce belongs here:

  * Bare acts from India Code (indiacode.nic.in). Central and State legislation
    is a government work; Section 52(1)(q) of the Copyright Act, 1957 permits
    reproduction of any Act and of judicial pronouncements.
  * Judgments from the Supreme Court and High Court portals, and eCourts.
  * Government guidance: NALSA, consumer helpline, parivahan, RTI portals.

Legal textbooks and commentaries — Ratanlal, Mulla, the SCC headnotes and
digests — are copyrighted. Do not ingest them. Beyond the obvious liability of
building a product on infringing content, they are also the wrong input: a
commentary is a scholar's argument *about* the bare act, and an assistant that
quotes it as though it were law is doing something worse than being unhelpful.
The authority is the section itself, which is free.
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path

from . import store
from .corpus import Passage

# ── Section splitting ───────────────────────────────────────────────────
# Indian bare acts number sections in a small number of recognisable shapes:
#
#   1. Short title, extent and commencement.—(1) This Act may be called…
#   304A. Causing death by negligence.—Whoever causes…
#   11.  Definitions
#
# The marginal note (the bit before the em dash) is the section's title, which
# is what makes a retrieved passage readable. Capture it when present.
_SECTION_RE = re.compile(
    r"""
    ^[ \t]*
    (?P<number>\d{1,4}[A-Z]{0,2})      # 1, 304A, 173, 66C
    \.[ \t]*
    (?P<rest>.*)$
    """,
    re.VERBOSE | re.MULTILINE,
)

_MARGINAL_NOTE_RE = re.compile(r"^(?P<note>[^.—–-]{3,120}?)\s*[.—–]\s*[—–(]")

_CHAPTER_RE = re.compile(r"^\s*CHAPTER\s+([IVXLC]+|\d+)\s*$", re.MULTILINE | re.IGNORECASE)

#: Boilerplate that carries no legal content and only dilutes retrieval.
_SKIP_MARKERS = (
    "arrangement of sections",
    "table of contents",
    "statement of objects and reasons",
    "printed by the manager",
    "government of india press",
)


def _clean(text: str) -> str:
    """Normalise the punctuation and whitespace of scraped or copy-pasted text."""
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("—", "—").replace("–", "–")
    # PDF extraction commonly leaves hyphenated line breaks mid-word.
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _slug(value: str, limit: int = 48) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return slug[:limit].rstrip("_")


def split_sections(text: str) -> list[tuple[str, str, str]]:
    """
    Split an act into (section number, marginal note, body).

    Returns them in document order. A section whose body is shorter than a
    sentence is dropped — those are almost always table-of-contents entries
    rather than the provision itself.
    """
    text = _clean(text)

    matches = list(_SECTION_RE.finditer(text))
    if not matches:
        return []

    sections: list[tuple[str, str, str]] = []
    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        block = text[start:end].strip()

        number = match.group("number")
        rest = match.group("rest").strip()

        note_match = _MARGINAL_NOTE_RE.match(rest)
        note = note_match.group("note").strip() if note_match else ""

        # Body is everything after the section number.
        body = block[len(number) + 1 :].strip()
        body = re.sub(r"\s*\n\s*", " ", body).strip()

        if len(body) < 80:
            continue
        if any(marker in body.lower()[:160] for marker in _SKIP_MARKERS):
            continue

        sections.append((number, note, body))

    return sections


def bare_act_to_passages(
    text: str,
    act_name: str,
    source_url: str,
    id_prefix: str,
    topics: tuple[str, ...] = (),
    max_chars: int = 2400,
) -> list[Passage]:
    """Turn the plain text of an act into one Passage per section."""
    passages: list[Passage] = []

    for number, note, body in split_sections(text):
        # A handful of sections (definitions, schedules of penalties) run very
        # long. Truncate on a sentence boundary rather than mid-clause, and say
        # so, since a silently cut-off legal provision is a trap.
        if len(body) > max_chars:
            cut = body.rfind(". ", 0, max_chars)
            body = body[: cut + 1 if cut > max_chars // 2 else max_chars]
            body += " […] (section continues — open the source for the full text)"

        title = f"{act_name} — Section {number}"
        if note:
            title = f"Section {number}: {note}"

        passages.append(
            Passage(
                id=f"{id_prefix}_s{number.lower()}",
                title=title,
                act=act_name,
                section=f"Section {number}",
                text=body,
                source_url=source_url,
                topics=topics + ((_slug(note, 40),) if note else ()),
            )
        )

    return passages


# ── Judgments ───────────────────────────────────────────────────────────
def judgment_to_passage(
    case_name: str,
    citation: str,
    holding: str,
    source_url: str,
    topics: tuple[str, ...] = (),
) -> Passage:
    """
    Record a judgment as its holding, not its full text.

    A Supreme Court judgment runs to tens of thousands of words, most of which
    is argument and procedural history. What a user needs — and what retrieval
    can actually rank — is the ratio: what was decided and what it means. Store
    that, and link to the full text.
    """
    return Passage(
        id=f"case_{_slug(case_name)}",
        title=case_name,
        act=case_name,
        section=citation,
        text=holding.strip(),
        source_url=source_url,
        topics=topics + ("judgment", "case law", "precedent"),
    )


# ── Commands ────────────────────────────────────────────────────────────
def cmd_bare_act(args: argparse.Namespace) -> int:
    path = Path(args.path)
    if not path.is_file():
        print(f"error: {path} not found", file=sys.stderr)
        return 1

    text = path.read_text(encoding="utf-8", errors="ignore")
    passages = bare_act_to_passages(
        text=text,
        act_name=args.act,
        source_url=args.url,
        id_prefix=args.name,
        topics=tuple(t.strip() for t in (args.topics or "").split(",") if t.strip()),
    )

    if not passages:
        print(
            "error: no sections recognised.\n"
            "The splitter expects lines beginning with a section number, as in\n"
            '  "173. Information in cognizable cases.—(1) Every information…"\n'
            "Check that the text is not a scanned image or a table of contents.",
            file=sys.stderr,
        )
        return 1

    written = store.write(args.name, passages)
    print(f"{len(passages)} sections → {written}")
    print("Rebuild the index by restarting the API, then run: python -m app.rag.eval")
    return 0


def cmd_list(_: argparse.Namespace) -> int:
    from .corpus import CORPUS

    counts = store.stats()
    ingested = sum(counts.values())
    print(f"\n  {len(CORPUS)} passages in the live index")
    print(f"    {len(CORPUS) - ingested} hand-written (app/rag/corpus*.py)")
    print(f"    {ingested} ingested (data/corpus/)\n")
    for name, count in counts.items():
        print(f"      {count:>6}  {name}")
    print()
    return 0


def cmd_refresh(_: argparse.Namespace) -> int:
    """
    Re-run every configured source.

    Sources are declared in `data/corpus/sources.txt`, one per line:

        name | act name | source url | local path or url

    Kept as a plain file rather than code so a scheduled job — a cron entry, a
    GitHub Action — can add a source without a deploy. Nothing here fetches the
    network automatically: an ingest that silently rewrites the legal corpus on
    a schedule is not something to enable without a person reviewing the diff.
    """
    manifest = store.STORE_DIR / "sources.txt"
    if not manifest.is_file():
        print(f"No manifest at {manifest} — nothing to refresh.")
        print("Create it with lines of the form:")
        print("  bns_2023 | Bharatiya Nyaya Sanhita, 2023 | https://… | data/raw/bns.txt")
        return 0

    failures = 0
    for line_number, line in enumerate(manifest.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) != 4:
            print(f"  line {line_number}: expected 4 fields, got {len(parts)} — skipped")
            failures += 1
            continue

        name, act, url, source = parts
        path = Path(source)
        if not path.is_file():
            print(f"  {name}: {source} not found — skipped")
            failures += 1
            continue

        passages = bare_act_to_passages(
            text=path.read_text(encoding="utf-8", errors="ignore"),
            act_name=act,
            source_url=url,
            id_prefix=name,
        )
        store.write(name, passages)
        print(f"  {name}: {len(passages)} sections")

    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="python -m app.rag.ingest",
        description="Ingest public legal sources into the retrieval corpus.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("bare-act", help="split an act's plain text into sections")
    p.add_argument("path", help="UTF-8 text file containing the act")
    p.add_argument("--name", required=True, help="store file name, e.g. bns_2023")
    p.add_argument("--act", required=True, help='full act name, e.g. "Bharatiya Nyaya Sanhita, 2023"')
    p.add_argument("--url", required=True, help="canonical source URL")
    p.add_argument("--topics", help="comma-separated topic tags applied to every section")
    p.set_defaults(func=cmd_bare_act)

    p = sub.add_parser("list", help="show what is in the store")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("refresh", help="re-run every source in sources.txt")
    p.set_defaults(func=cmd_refresh)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
