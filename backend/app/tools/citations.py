"""
Citation extractor.

Reading a judgment and listing everything it relies on is done with a
highlighter and a legal pad in most chambers. It is pure pattern recognition,
which makes it a poor use of a person and a good use of a regex.

Given a judgment, a brief or an opinion, this pulls out:

  * **Case citations** — reported (2017) 8 SCC 746, AIR 1973 SC 1461, neutral
    citations like 2023 INSC 456, and case names in the "A v. B" form.
  * **Statutory references** — Section 138 of the Negotiable Instruments Act,
    Article 21, Order VII Rule 11.

Statutory references are matched against the retrieval corpus, so a reference
the assistant can explain becomes a link rather than a string.

Deliberately conservative: it would rather miss an unusual citation format than
report a false one, because a fabricated citation in a legal document is worse
than an incomplete list.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# ── Reported citations ──────────────────────────────────────────────────
#: (2017) 8 SCC 746 · (1973) 4 SCC 225 · (1997) 1 SCC 416
_SCC_RE = re.compile(r"\(\s*(19|20)\d{2}\s*\)\s*\d{1,2}\s+[A-Z]{2,6}(?:\s+\(\w+\))?\s+\d{1,5}")

#: AIR 1973 SC 1461 · AIR 2018 SC 4321
_AIR_RE = re.compile(r"\bAIR\s+(?:19|20)\d{2}\s+[A-Z]{2,6}\s+\d{1,5}")

#: Neutral citations: 2023 INSC 456, 2024 SCC OnLine Del 1234
_NEUTRAL_RE = re.compile(
    r"\b(?:19|20)\d{2}\s+(?:INSC|SCC\s+OnLine\s+[A-Z][a-z]{1,4}|[A-Z]{2,5}HC)\s+\d{1,6}"
)

#: Case names. Requires " v. " or " vs " with capitalised parties on both
#: sides — loose enough to catch real names, tight enough to avoid prose.
_CASE_NAME_RE = re.compile(
    r"\b([A-Z][\w.&'-]*(?:\s+[A-Z][\w.&'-]*){0,5})"
    r"\s+(?:v\.?|vs\.?|versus)\s+"
    r"([A-Z][\w.&'-]*(?:\s+[A-Z][\w.&'-]*){0,5})",
)

# ── Statutory references ────────────────────────────────────────────────
_SECTION_RE = re.compile(
    r"\b(?P<kind>Sections?|Secs?\.?|Articles?|Arts?\.?|Rules?|Orders?|Clauses?)\s+"
    r"(?P<number>\d{1,4}[A-Z]{0,2}(?:\s*\(\s*\w{1,3}\s*\))*)"
    r"(?:\s*(?:read\s+with|r/w|and|,)\s*\d{1,4}[A-Z]{0,2})*"
    r"(?:\s+of\s+(?:the\s+)?(?P<act>[A-Z](?:[\w,'()\-]|\.(?!\s)|[ ](?![ ])){0,80}?(?:Act|Sanhita|Adhiniyam|Code|Constitution)(?:,?\s*\d{4})?)(?=[\s,.;:)]|$))?",
    re.IGNORECASE,
)

#: Common short forms people write instead of the full act name.
_ACT_ALIASES = {
    "ipc": "Indian Penal Code, 1860",
    "crpc": "Code of Criminal Procedure, 1973",
    "cpc": "Code of Civil Procedure, 1908",
    "bns": "Bharatiya Nyaya Sanhita, 2023",
    "bnss": "Bharatiya Nagarik Suraksha Sanhita, 2023",
    "bsa": "Bharatiya Sakshya Adhiniyam, 2023",
    "ni act": "Negotiable Instruments Act, 1881",
    "it act": "Information Technology Act, 2000",
    "rti act": "Right to Information Act, 2005",
    "hma": "Hindu Marriage Act, 1955",
    "mv act": "Motor Vehicles Act, 1988",
    "cpa": "Consumer Protection Act, 2019",
}

_ALIAS_RE = re.compile(
    r"\b(?P<kind>Sections?|Secs?\.?|Articles?|Arts?\.?)\s+"
    r"(?P<number>\d{1,4}[A-Z]{0,2}(?:\s*\(\s*\w{1,3}\s*\))*)\s*"
    r"(?:of\s+(?:the\s+)?)?"
    r"(?P<alias>IPC|CrPC|CPC|BNSS|BNS|BSA|NI\s+Act|IT\s+Act|RTI\s+Act|HMA|MV\s+Act|CPA)\b",
    re.IGNORECASE,
)

#: Sentences that merely mention a citation in passing versus rely on it.
_RELIANCE_MARKERS = (
    "relied", "held", "laid down", "followed", "applied", "referred",
    "observed", "reiterated", "affirmed", "distinguished", "overruled",
)


@dataclass
class Citation:
    text: str
    kind: str  # case | statute
    #: Where in the document it appears, so the user can find it.
    context: str = ""
    count: int = 1
    #: For statutes: the normalised act name, when resolvable.
    act: str | None = None
    section: str | None = None
    #: Corpus passage id, when the assistant can explain this provision.
    passage_id: str | None = None
    passage_title: str | None = None
    #: True where the surrounding sentence suggests the court relied on it.
    relied_on: bool = False


@dataclass
class ExtractionResult:
    cases: list[Citation] = field(default_factory=list)
    statutes: list[Citation] = field(default_factory=list)
    word_count: int = 0
    #: Statutes with no matching corpus passage — candidates for ingestion.
    unresolved: list[str] = field(default_factory=list)


def _sentence_around(text: str, start: int, end: int, width: int = 160) -> str:
    """A readable slice of the sentence a match sits in."""
    left = max(0, start - width // 2)
    right = min(len(text), end + width // 2)
    snippet = " ".join(text[left:right].split())
    return ("…" if left > 0 else "") + snippet + ("…" if right < len(text) else "")


def _relied(context: str) -> bool:
    lowered = context.lower()
    return any(marker in lowered for marker in _RELIANCE_MARKERS)


def _normalise(value: str) -> str:
    return " ".join(value.split()).strip(" .,;:")


#: Words that begin a sentence introducing a case and get swept into the name.
_CASE_LEAD_WORDS = {
    "in", "see", "the", "and", "cf", "per", "vide", "also", "following",
    "citing", "relying", "on", "to", "of", "from", "but", "however",
}


def _strip_lead(name: str) -> str:
    """Remove sentence connectives captured ahead of a party name."""
    words = name.split()
    while words and words[0].lower().strip(".,") in _CASE_LEAD_WORDS:
        words.pop(0)
    return " ".join(words)


def _resolve_passage(act: str | None, section: str | None) -> tuple[str | None, str | None]:
    """
    Find a corpus passage explaining this provision.

    Matches on act name and section number rather than free text, so a hit
    means the passage genuinely covers the provision cited.
    """
    if not act and not section:
        return None, None

    from app.rag.corpus import CORPUS

    # "the Constitution" must match the passage act "Constitution of India".
    act_key = re.sub(r"^(the|of the)\s+", "", (act or "").lower().strip())
    section_key = (section or "").lower().replace(" ", "")

    # Compare section numbers as whole tokens. Substring matching links
    # "Section 12" to a passage whose alias is "Section 125 CrPC", which is a
    # confidently wrong citation — the exact failure mode this guards against.
    def tokenised(value: str) -> str:
        """Split on non-alphanumerics and pad, so numbers compare as tokens."""
        return " " + " ".join(re.split(r"[^0-9a-z]+", value.lower())).strip() + " "

    needle = f" {' '.join(re.split(r'[^0-9a-z]+', section_key)).strip()} " if section_key else ""

    def section_matches(haystack: str) -> bool:
        return bool(needle) and needle in haystack

    best: tuple[int, str, str] | None = None
    for passage in CORPUS:
        score = 0
        passage_act = passage.act.lower()
        section_hit = section_matches(tokenised(passage.section))

        if act_key and (act_key in passage_act or passage_act in act_key):
            score += 3
        if section_hit:
            score += 2

        # An alias carries both the number and its act ("Section 498A IPC"), so
        # matching one is strong evidence on its own.
        for alias in passage.also_known_as:
            if section_matches(tokenised(alias)):
                score += 5

        if score > (best[0] if best else 0):
            best = (score, passage.id, passage.title)

    # A bare section number is not enough. "Rule 11" appears in dozens of
    # statutes, and linking it to whichever passage happens to have a Section 11
    # produces a confident, wrong citation — the exact failure this tool exists
    # to prevent. Require the act to corroborate, or an alias that names it.
    if best is None or best[0] < 5:
        return None, None
    return best[1], best[2]


def extract(text: str) -> ExtractionResult:
    """Pull every citation out of a judgment or brief."""
    result = ExtractionResult(word_count=len(text.split()))

    # ── Cases ──
    seen_cases: dict[str, Citation] = {}
    #: First span and pattern kind per case, so a name and the citation that
    #: follows it can be recognised afterwards as one authority.
    spans: dict[str, tuple[int, int, str]] = {}
    for pattern, kind in (
        (_SCC_RE, "reported"),
        (_AIR_RE, "reported"),
        (_NEUTRAL_RE, "neutral"),
        (_CASE_NAME_RE, "name"),
    ):
        for match in pattern.finditer(text):
            raw = _normalise(match.group(0))
            if kind == "name":
                raw = _strip_lead(raw)
            if len(raw) < 6:
                continue
            key = raw.lower()
            if key in seen_cases:
                seen_cases[key].count += 1
                continue
            context = _sentence_around(text, match.start(), match.end())
            seen_cases[key] = Citation(
                text=raw,
                kind="case",
                context=context,
                relied_on=_relied(context),
            )
            spans[key] = (match.start(), match.end(), kind)

    # A judgment cites a case once, as "Name v. Name, (2017) 14 SCC 200" — but
    # the name pattern and the reported-citation pattern each match a part of
    # it, so it arrives here as two entries. Join them where the citation
    # directly follows the name, which is the only place it can sit and still
    # belong to it. Anything further away is left alone: two authorities
    # reported as one is a worse error than one reported as two.
    merged: set[str] = set()
    for name_key, (_, name_end, name_kind) in spans.items():
        if name_kind != "name":
            continue
        for cite_key, (cite_start, _, cite_kind) in spans.items():
            if cite_kind == "name" or cite_key in merged:
                continue
            if not 0 <= cite_start - name_end <= 3:
                continue
            gap = text[name_end:cite_start]
            if "." in gap:
                continue
            # The sentence-ending full stop is usually captured *inside* the
            # name match ("…Ram v. Shyam."), so looking only at the gap misses
            # it and the next sentence's citation gets attached to this case.
            # A full stop followed by nothing but space ends the sentence; one
            # followed by a comma is an abbreviation, as in "State of U.P.,".
            bridge = text[max(name_end - 1, 0):cite_start]
            if not re.fullmatch(r"\.\s*", bridge):
                name = seen_cases[name_key]
                citation = seen_cases[cite_key]
                name.text = f"{name.text}, {citation.text}"
                name.count = max(name.count, citation.count)
                name.relied_on = name.relied_on or citation.relied_on
                merged.add(cite_key)
                break
    for key in merged:
        del seen_cases[key]

    # ── Statutes ──
    seen_statutes: dict[str, Citation] = {}

    def add_statute(raw: str, section: str, act: str | None, start: int, end: int) -> None:
        key = f"{(act or '').lower()}|{section.lower()}"
        if key in seen_statutes:
            seen_statutes[key].count += 1
            return
        context = _sentence_around(text, start, end)
        passage_id, passage_title = _resolve_passage(act, section)
        seen_statutes[key] = Citation(
            text=_normalise(raw),
            kind="statute",
            context=context,
            act=act,
            section=section,
            passage_id=passage_id,
            passage_title=passage_title,
            relied_on=_relied(context),
        )

    # Short forms first, so "Section 138 NI Act" resolves to the full name
    # before the generic pattern sees it without one.
    for match in _ALIAS_RE.finditer(text):
        alias = _normalise(match.group("alias")).lower()
        add_statute(
            match.group(0),
            _normalise(match.group("number")),
            _ACT_ALIASES.get(alias, alias.upper()),
            match.start(),
            match.end(),
        )

    for match in _SECTION_RE.finditer(text):
        act = match.group("act")
        add_statute(
            match.group(0),
            _normalise(match.group("number")),
            _normalise(act) if act else None,
            match.start(),
            match.end(),
        )

    # Where the same section was seen both with and without its act name,
    # keep only the richer entry so the list does not double-report it.
    by_section: dict[str, Citation] = {}
    for citation in seen_statutes.values():
        key = (citation.section or "").lower()
        existing = by_section.get(key)
        if existing is None:
            by_section[key] = citation
        elif citation.act and not existing.act:
            citation.count += existing.count
            by_section[key] = citation
        else:
            existing.count += citation.count
    seen_statutes = {f"k{i}": c for i, c in enumerate(by_section.values())}

    result.cases = sorted(seen_cases.values(), key=lambda c: (-c.count, c.text))
    result.statutes = sorted(
        seen_statutes.values(), key=lambda c: (c.passage_id is None, -c.count, c.text)
    )
    result.unresolved = [
        c.text for c in result.statutes if c.passage_id is None and c.act
    ][:20]
    return result
