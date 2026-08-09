"""
Document analysis, grounded and local-first.

Three ideas make this fast enough to run on a laptop model:

1. **Don't ask a model what a regex knows.** Counts, dates, monetary amounts and
   statutory references are extracted deterministically. They are also more
   accurate that way — a language model miscounts words.

2. **Don't send the whole document.** A lease is mostly boilerplate. Salient
   selection keeps the opening, the clause-dense regions and anything near a
   risk term, and drops the rest, so the model sees a few thousand characters
   instead of fifty thousand.

3. **Don't analyse the same file twice.** Results are cached on a hash of the
   text and the output language.

Legal citations come from retrieval over `corpus.py`, not from the model, so a
clause flagged as risky points at a real provision the reader can open.
"""

from __future__ import annotations

import asyncio
import hashlib
import os
import re
import time
from collections import OrderedDict
from typing import Any

from pydantic import BaseModel, Field

from .retriever import RetrievedPassage, get_retriever

# ── Schema ──────────────────────────────────────────────────────────────
class ClauseItem(BaseModel):
    title: str
    content: str
    risk_level: str = Field(description="one of: low, medium, high")


class SourceRef(BaseModel):
    title: str
    citation: str
    url: str


class AnalysisResult(BaseModel):
    summary: str
    document_type: str
    word_count: int = 0
    char_count: int = 0
    clauses: list[ClauseItem] = []
    key_entities: list[str] = []
    risk_flags: list[str] = []
    recommendations: list[str] = []
    #: Concrete next steps, in order. Added for readers who need to act, not study.
    action_steps: list[str] = []
    #: Dates and periods found in the text that may be deadlines.
    key_dates: list[str] = []
    #: Statute passages the analysis was grounded in.
    sources: list[SourceRef] = []
    #: ollama | gemini | heuristic
    provider: str = "heuristic"
    #: True while a model is still enriching this result in the background.
    #: The client polls /api/analyze/refine/{refine_id} and swaps it in.
    refining: bool = False
    refine_id: str | None = None


#: The model is asked only for the fields it is actually good at. Counts,
#: dates and sources are filled in from deterministic extraction afterwards.
class _ModelPortion(BaseModel):
    summary: str
    document_type: str
    clauses: list[ClauseItem] = []
    key_entities: list[str] = []
    risk_flags: list[str] = []
    recommendations: list[str] = []
    action_steps: list[str] = []


# ── Deterministic extraction ────────────────────────────────────────────
_DATE_PATTERNS = [
    r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
    r"\b\d{1,2}(?:st|nd|rd|th)?\s+(?:January|February|March|April|May|June|July|"
    r"August|September|October|November|December)\s+\d{4}\b",
    r"\b(?:January|February|March|April|May|June|July|August|September|October|"
    r"November|December)\s+\d{1,2},?\s+\d{4}\b",
]
_PERIOD_RE = re.compile(
    r"\b(?:within|not later than|before the expiry of|no later than)\s+"
    r"(\w+(?:[- ]\w+)?)\s+(day|days|week|weeks|month|months|year|years)\b",
    re.IGNORECASE,
)
_MONEY_RE = re.compile(
    r"(?:₹|Rs\.?|INR|USD|\$)\s?[\d,]+(?:\.\d{1,2})?(?:\s?(?:lakh|lakhs|crore|crores|million|billion))?",
    re.IGNORECASE,
)
_SECTION_RE = re.compile(
    r"\b(?:Section|Sec\.?|Article|Art\.?|Clause|Rule|Order)\s+\d+[A-Za-z]?(?:\(\d+\))?",
    re.IGNORECASE,
)
_PARTY_RE = re.compile(
    r"\b(?:M/s\.?\s+[A-Z][\w&.\- ]{2,50}"
    r"|[A-Z][\w.\-]+(?:\s+[A-Z][\w.\-]+){0,3}\s+(?:Private\s+Limited|Pvt\.?\s*Ltd\.?|Limited|Ltd\.?|LLP|Inc\.?|Corporation))"
)

#: Drafting connectives that sit in front of a party name in capitals and would
#: otherwise be captured as part of it ("BETWEEN Sharma Properties Ltd").
_PARTY_LEAD_WORDS = {
    "between", "and", "whereas", "the", "this", "by", "with", "to", "of",
    "hereinafter", "namely", "viz",
}

#: Risk vocabulary, weighted. Ordered most severe first.
_RISK_TERMS: list[tuple[str, tuple[str, ...]]] = [
    ("high", (
        "indemnif", "personal guarantee", "liquidated damages", "penalty",
        "forfeit", "irrevocable", "non-compete", "restraint of trade",
        "waive any right", "waives all", "without notice", "sole discretion",
        "unlimited liability", "specific performance", "lien on",
    )),
    ("medium", (
        "terminate", "termination", "arbitration", "exclusive jurisdiction",
        "late fee", "interest at", "lock-in", "notice period", "auto-renew",
        "confidential", "assign", "escalation", "security deposit", "breach",
    )),
    ("low", (
        "governing law", "definitions", "entire agreement", "severability",
        "force majeure", "amendment", "counterparts",
    )),
]

_DOC_TYPES: list[tuple[str, tuple[str, ...]]] = [
    ("Rent / Lease Agreement", ("lessor", "lessee", "tenant", "landlord", "rent", "tenancy", "leave and licence")),
    ("Employment Agreement", ("employer", "employee", "appointment", "probation", "ctc", "designation", "resignation")),
    ("Loan / Facility Agreement", ("borrower", "lender", "principal amount", "emi", "repayment", "interest rate", "collateral")),
    ("Court Judgment / Order", ("hon'ble", "petitioner", "respondent", "writ petition", "appellant", "coram", "it is ordered")),
    ("First Information Report", ("first information report", "fir no", "police station", "cognizable", "u/s")),
    ("Legal Notice", ("legal notice", "my client", "hereby call upon", "failing which", "advocate")),
    ("Sale Deed / Conveyance", ("sale deed", "vendor", "purchaser", "conveyance", "sub-registrar", "schedule of property")),
    ("Will / Testament", ("last will", "testament", "bequeath", "executor", "legatee")),
    ("Power of Attorney", ("power of attorney", "attorney holder", "constitute and appoint")),
    ("Non-Disclosure Agreement", ("non-disclosure", "confidential information", "disclosing party", "receiving party")),
    ("Service / Vendor Agreement", ("service provider", "scope of work", "deliverables", "statement of work")),
]


def precompute(text: str) -> dict[str, Any]:
    """Facts a regex knows better than a language model."""
    dates: list[str] = []
    for pattern in _DATE_PATTERNS:
        dates.extend(re.findall(pattern, text, re.IGNORECASE))

    periods = [
        f"within {m.group(1)} {m.group(2)}" for m in _PERIOD_RE.finditer(text)
    ]

    amounts = _MONEY_RE.findall(text)
    sections = _SECTION_RE.findall(text)

    parties: list[str] = []
    for match in _PARTY_RE.findall(text):
        words = match.split()
        while words and words[0].lower().strip(",.") in _PARTY_LEAD_WORDS:
            words.pop(0)
        if words:
            parties.append(" ".join(words))

    def unique(items: list[str], limit: int) -> list[str]:
        seen: list[str] = []
        for item in items:
            cleaned = " ".join(item.split())
            if cleaned and cleaned not in seen:
                seen.append(cleaned)
            if len(seen) >= limit:
                break
        return seen

    return {
        "word_count": len(text.split()),
        "char_count": len(text),
        "key_dates": unique(dates + periods, 10),
        "amounts": unique(amounts, 8),
        "section_refs": unique(sections, 12),
        "parties": unique(parties, 8),
    }


def detect_document_type(text: str) -> str:
    lowered = text.lower()
    best, best_score = "Legal Document", 0
    for label, markers in _DOC_TYPES:
        score = sum(1 for m in markers if m in lowered)
        if score > best_score:
            best, best_score = label, score
    return best


def select_salient(text: str, budget: int = 6000) -> str:
    """
    Reduce a long document to the parts worth reading.

    Keeps the opening (parties, recitals and dates live there), then the
    paragraphs containing risk vocabulary, statutory references or money.
    A twelve-page lease collapses to a couple of thousand characters without
    losing anything a risk analysis would act on.
    """
    if len(text) <= budget:
        return text

    head = text[: budget // 3]
    remainder = text[budget // 3 :]

    paragraphs = re.split(r"\n\s*\n|\r\n\s*\r\n", remainder)
    all_terms = [t for _, terms in _RISK_TERMS for t in terms]

    def salience(paragraph: str) -> int:
        low = paragraph.lower()
        score = sum(2 for term in all_terms if term in low)
        score += 2 * len(_SECTION_RE.findall(paragraph))
        score += len(_MONEY_RE.findall(paragraph))
        return score

    scored = sorted(
        ((salience(p), i, p) for i, p in enumerate(paragraphs) if p.strip()),
        key=lambda t: (-t[0], t[1]),
    )

    kept: list[tuple[int, str]] = []
    used = len(head)
    for score, index, paragraph in scored:
        if score <= 0:
            continue
        if used + len(paragraph) > budget:
            continue
        kept.append((index, paragraph))
        used += len(paragraph)

    kept.sort(key=lambda t: t[0])
    body = "\n\n".join(p for _, p in kept)
    return f"{head}\n\n[…]\n\n{body}" if body else head


def heuristic_clauses(text: str) -> list[ClauseItem]:
    """
    Split the document into clauses and grade each by its risk vocabulary.

    This is the no-model path. It is blunt, but it never invents a clause that
    is not in the document, which is the property that matters here.
    """
    chunks = re.split(r"\n\s*(?=\d{1,2}[.)]\s+[A-Z]|[A-Z][A-Z \-]{6,}\n)", text)
    if len(chunks) < 2:
        chunks = [c for c in re.split(r"\n\s*\n", text) if len(c.strip()) > 80]

    clauses: list[ClauseItem] = []
    for chunk in chunks:
        stripped = chunk.strip()
        if len(stripped) < 60:
            continue

        lowered = stripped.lower()
        level = "low"
        for candidate, terms in _RISK_TERMS:
            if any(term in lowered for term in terms):
                level = candidate
                break

        first_line = stripped.split("\n", 1)[0].strip()
        title = (first_line[:70] + "…") if len(first_line) > 70 else first_line
        body = " ".join(stripped.split())
        clauses.append(
            ClauseItem(
                title=title or "Clause",
                content=(body[:420] + "…") if len(body) > 420 else body,
                risk_level=level,
            )
        )
        if len(clauses) >= 10:
            break

    order = {"high": 0, "medium": 1, "low": 2}
    clauses.sort(key=lambda c: order.get(c.risk_level, 3))
    return clauses


def heuristic_risk_flags(text: str) -> list[str]:
    lowered = text.lower()
    flags: list[str] = []
    explanations = {
        "indemnif": "Contains an indemnity — you may be liable for the other party's losses.",
        "personal guarantee": "A personal guarantee puts your own assets at risk, not just the company's.",
        "liquidated damages": "Pre-agreed damages are payable on breach without proof of actual loss.",
        "non-compete": "A restraint on future work. Post-employment restraints are largely unenforceable in India under Section 27 of the Indian Contract Act.",
        "sole discretion": "One party decides unilaterally; you have limited recourse.",
        "without notice": "An action can be taken against you with no warning period.",
        "irrevocable": "Something granted here cannot be withdrawn later.",
        "arbitration": "Disputes go to arbitration rather than court — check the seat, cost and who appoints the arbitrator.",
        "exclusive jurisdiction": "Disputes must be filed in a named city, which may be far from you.",
        "lock-in": "You are committed for a minimum period and may pay to exit early.",
        "auto-renew": "The agreement renews itself unless you actively cancel.",
        "forfeit": "A deposit or payment may be kept by the other party.",
    }
    for marker, explanation in explanations.items():
        if marker in lowered:
            flags.append(explanation)
    return flags[:8]


# ── Retrieval grounding ─────────────────────────────────────────────────
def relevant_law(text: str, doc_type: str, limit: int = 3) -> list[RetrievedPassage]:
    """Find statute passages relevant to this document."""
    retriever = get_retriever()
    # Query on the document type plus its most distinctive vocabulary; the raw
    # text is too long and too boilerplate-heavy to retrieve well.
    lowered = text.lower()
    signals = [
        term
        for _, terms in _RISK_TERMS
        for term in terms
        if term in lowered
    ][:8]
    query = f"{doc_type} {' '.join(signals)}"
    return get_retriever().search(query, top_k=limit, min_score=0.30) if retriever else []


# ── Cache ───────────────────────────────────────────────────────────────
_CACHE: OrderedDict[str, AnalysisResult] = OrderedDict()
_CACHE_LIMIT = 64


def _cache_key(text: str, language: str) -> str:
    digest = hashlib.sha256(text.encode("utf-8", "ignore")).hexdigest()
    return f"{digest}:{language}"


def _cache_get(key: str) -> AnalysisResult | None:
    result = _CACHE.get(key)
    if result is not None:
        _CACHE.move_to_end(key)
    return result


def _cache_put(key: str, value: AnalysisResult) -> None:
    _CACHE[key] = value
    _CACHE.move_to_end(key)
    while len(_CACHE) > _CACHE_LIMIT:
        _CACHE.popitem(last=False)


# ── Prompt ──────────────────────────────────────────────────────────────
def _build_prompt(
    excerpt: str, facts: dict[str, Any], doc_type: str, law: list[RetrievedPassage], language: str
) -> str:
    statutes = "\n".join(
        f"- {p.passage.citation}: {p.passage.text[:260]}" for p in law
    ) or "- (no directly matching provision retrieved)"

    return f"""You are a careful Indian legal analyst. Explain this document to a
non-lawyer who needs to understand what they are agreeing to or facing.

Write everything in {language}.

Rules:
- Explain in plain words. No Latin, no jargon without a gloss.
- Only describe what is actually in the excerpt. Do not invent clauses, parties,
  amounts or dates.
- When you cite law, use ONLY the provisions listed under REFERENCE LAW below.
  If none fit, cite nothing rather than guessing a section number.
- risk_level must be exactly one of: low, medium, high.
- action_steps are concrete things the reader should do next, in order.
- Be concise. Five clauses at most, the ones that actually matter.

DETECTED TYPE: {doc_type}
PARTIES FOUND: {', '.join(facts['parties']) or 'none detected'}
AMOUNTS FOUND: {', '.join(facts['amounts']) or 'none detected'}
DATES/DEADLINES FOUND: {', '.join(facts['key_dates']) or 'none detected'}

REFERENCE LAW
{statutes}

DOCUMENT EXCERPT
{excerpt}
"""


# ── Providers ───────────────────────────────────────────────────────────
#: How long to let the local model run before giving up and shipping the
#: deterministic analysis instead. A 26B model on a laptop takes well over a
#: minute; nobody waits that long staring at a spinner, and the heuristic
#: result is already useful. Raise it if you would rather wait.
ANALYZE_BUDGET_SECONDS = float(os.environ.get("ANALYZE_BUDGET_SECONDS", "45"))

#: The background refinement runs after the reader already has an answer, so it
#: can afford to wait for a large model. Only the blocking path is impatient.
ANALYZE_REFINE_BUDGET_SECONDS = float(
    os.environ.get("ANALYZE_REFINE_BUDGET_SECONDS", "420")
)

#: Keep the weights resident between requests so only the first call pays the
#: load cost. Without this Ollama evicts the model after five minutes idle and
#: every analysis is a cold start.
OLLAMA_KEEP_ALIVE = os.environ.get("OLLAMA_KEEP_ALIVE", "15m")


async def _ollama_structured(
    prompt: str, budget: float = ANALYZE_BUDGET_SECONDS
) -> _ModelPortion | None:
    """
    Ask the local model for JSON matching our schema.

    Ollama constrains decoding to the schema, so the reply parses reliably
    rather than needing the "strip the markdown fence and pray" dance.
    """
    from .engine import OLLAMA_URL, _resolve_ollama_model

    model = await _resolve_ollama_model()
    if not model:
        return None

    import httpx

    try:
        async with httpx.AsyncClient(timeout=budget) as client:
            response = await client.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    # Reasoning traces are pure latency here: the schema already
                    # forces the shape and the law comes from retrieval.
                    "think": False,
                    "format": _ModelPortion.model_json_schema(),
                    "keep_alive": OLLAMA_KEEP_ALIVE,
                    "options": {"temperature": 0.1, "num_predict": 900},
                },
            )
            response.raise_for_status()
            raw = (response.json().get("response") or "").strip()
            return _ModelPortion.model_validate_json(raw) if raw else None
    except httpx.TimeoutException:
        print(
            f"[analyze] Local model exceeded its {budget:.0f}s budget. Keeping the "
            f"deterministic analysis — pull a smaller model (ollama pull gemma3:4b) "
            f"for interactive speed."
        )
        return None
    except Exception as exc:
        print(f"[analyze] Local model failed ({type(exc).__name__}): {exc}")
        return None


async def _gemini_structured(prompt: str) -> _ModelPortion | None:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key or api_key == "your_api_key_here" or len(api_key) < 20:
        return None

    def _call() -> _ModelPortion | None:
        try:
            from google import genai

            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model=os.environ.get("GEMINI_MODEL", "gemini-2.0-flash"),
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": _ModelPortion,
                    "temperature": 0.1,
                },
            )
            return _ModelPortion.model_validate_json(response.text)
        except Exception as exc:
            print(f"[analyze] Gemini failed: {exc}")
            return None

    return await asyncio.to_thread(_call)


# ── Assembly ────────────────────────────────────────────────────────────
def _prepare(text: str, language: str) -> dict[str, Any]:
    """Everything both the fast path and the model path need, computed once."""
    facts = precompute(text)
    doc_type = detect_document_type(text)
    law = relevant_law(text, doc_type)
    excerpt = select_salient(text)
    return {
        "facts": facts,
        "doc_type": doc_type,
        "law": law,
        "excerpt": excerpt,
        "language": language,
        "sources": [
            SourceRef(
                title=p.passage.title,
                citation=p.passage.citation,
                url=p.passage.source_url,
            )
            for p in law
        ],
        "prompt": _build_prompt(excerpt, facts, doc_type, law, language),
    }


_BASE_RECOMMENDATIONS = [
    "Read every clause marked high risk before you sign.",
    "Keep a signed copy, and proof of delivery for any notice you send.",
    "Free legal aid is available on 15100 if you cannot afford a lawyer.",
]


def _deterministic_result(text: str, prepared: dict[str, Any]) -> AnalysisResult:
    """The analysis the document yields on its own, with no model involved."""
    facts, doc_type = prepared["facts"], prepared["doc_type"]
    return AnalysisResult(
        summary=(
            f"This appears to be a {doc_type.lower()} of about "
            f"{facts['word_count']:,} words. The breakdown below comes straight from "
            f"the text: clauses are shown as they appear and graded by the risk "
            f"vocabulary they contain. Start with the clauses marked high."
        ),
        document_type=doc_type,
        clauses=heuristic_clauses(text),
        key_entities=facts["parties"] + facts["amounts"],
        risk_flags=heuristic_risk_flags(text),
        recommendations=list(_BASE_RECOMMENDATIONS),
        action_steps=[],
    )


def _apply_facts(result: AnalysisResult, prepared: dict[str, Any], provider: str) -> None:
    """Deterministic facts always win over anything a model said."""
    facts = prepared["facts"]
    result.word_count = facts["word_count"]
    result.char_count = facts["char_count"]
    result.key_dates = facts["key_dates"]
    result.sources = prepared["sources"]
    result.provider = provider
    result.refining = False
    result.refine_id = None


def _merge(portion: _ModelPortion, text: str, prepared: dict[str, Any]) -> AnalysisResult:
    """
    Fold the model's contribution into the deterministic analysis.

    Every field falls back rather than replacing, so a model that returns an
    empty `clauses` array — which happens, schema or no schema — cannot produce
    a page with an empty section on it.
    """
    base = _deterministic_result(text, prepared)
    allowed = {"low", "medium", "high"}
    model_clauses = [
        ClauseItem(
            title=c.title,
            content=c.content,
            risk_level=c.risk_level.lower() if c.risk_level.lower() in allowed else "medium",
        )
        for c in portion.clauses
        if c.title.strip() and c.content.strip()
    ]
    return AnalysisResult(
        summary=portion.summary.strip() or base.summary,
        document_type=portion.document_type or base.document_type,
        clauses=model_clauses or base.clauses,
        key_entities=portion.key_entities or base.key_entities,
        risk_flags=portion.risk_flags or base.risk_flags,
        recommendations=portion.recommendations or base.recommendations,
        action_steps=portion.action_steps,
    )


async def _any_model_available() -> bool:
    """Is there any generator at all? Decides whether to bother refining."""
    from .engine import _resolve_ollama_model

    if await _resolve_ollama_model():
        return True
    api_key = os.environ.get("GEMINI_API_KEY")
    return bool(api_key and api_key != "your_api_key_here" and len(api_key) >= 20)


async def _run_model(
    prompt: str, budget: float = ANALYZE_BUDGET_SECONDS
) -> tuple[_ModelPortion | None, str]:
    portion = await _ollama_structured(prompt, budget)
    if portion is not None:
        return portion, "ollama"
    portion = await _gemini_structured(prompt)
    if portion is not None:
        return portion, "gemini"
    return None, "heuristic"


async def _blocking_model_pass(
    key: str, text: str, prepared: dict[str, Any], started: float
) -> AnalysisResult:
    portion, provider = await _run_model(prepared["prompt"])
    result = (
        _merge(portion, text, prepared)
        if portion is not None
        else _deterministic_result(text, prepared)
    )
    _apply_facts(result, prepared, provider)
    print(
        f"[analyze] {provider} · {prepared['facts']['word_count']:,} words → "
        f"{len(prepared['excerpt']):,} char excerpt · {time.perf_counter() - started:.1f}s"
    )
    _cache_put(key, result)
    return result


# ── Background refinement ───────────────────────────────────────────────
#: Refinement jobs in flight, keyed by cache key. A local model can take a
#: minute; making the reader watch a spinner for that long is a worse product
#: than showing them the deterministic analysis immediately and upgrading it.
_JOBS: dict[str, "asyncio.Task[AnalysisResult | None]"] = {}


async def _refine_job(key: str, text: str, language: str) -> AnalysisResult | None:
    """Run the model behind an already-delivered response."""
    started = time.perf_counter()
    try:
        prepared = _prepare(text, language)
        portion, provider = await _run_model(
            prepared["prompt"], ANALYZE_REFINE_BUDGET_SECONDS
        )
        if portion is None:
            # No usable model output: settle the cache on the deterministic
            # result so the client stops polling.
            settled = _deterministic_result(text, prepared)
            _apply_facts(settled, prepared, "heuristic")
            _cache_put(key, settled)
            return settled

        result = _merge(portion, text, prepared)
        _apply_facts(result, prepared, provider)
        _cache_put(key, result)
        print(f"[analyze] refined via {provider} in {time.perf_counter() - started:.1f}s")
        return result
    except Exception as exc:
        print(f"[analyze] refinement error: {exc}")
        return None


async def get_refinement(refine_id: str) -> tuple[str, AnalysisResult | None]:
    """
    Poll a background refinement.

    Returns ("ready", result) once the model has finished, ("pending", None)
    while it is still working, or ("gone", None) if the id is unknown — which
    also covers a server restart, so the client stops polling.
    """
    finished = _cache_get(refine_id)
    if finished is not None and not finished.refining:
        return "ready", finished

    task = _JOBS.get(refine_id)
    if task is None:
        return "gone", None
    if not task.done():
        return "pending", None

    _JOBS.pop(refine_id, None)
    try:
        result = task.result()
    except Exception as exc:
        print(f"[analyze] refinement failed: {exc}")
        return "gone", None
    return ("ready", result) if result else ("gone", None)


# ── Entry point ─────────────────────────────────────────────────────────
async def analyze_document(
    text: str, language: str = "English", allow_background: bool = True
) -> AnalysisResult:
    """
    Analyse a legal document, preferring local compute at every step.

    With `allow_background`, the deterministic analysis is returned straight
    away and a model refinement continues behind it. Set it False to block
    until the model answers (used by the background task itself, and useful
    for scripted runs).
    """
    key = _cache_key(text, language)
    cached = _cache_get(key)
    if cached is not None and not cached.refining:
        print("[analyze] cache hit")
        return cached

    started = time.perf_counter()
    prepared = _prepare(text, language)

    base = _deterministic_result(text, prepared)
    _apply_facts(base, prepared, provider="heuristic")

    model_available = await _any_model_available()

    if not model_available:
        print(
            f"[analyze] heuristic · {prepared['facts']['word_count']:,} words · "
            f"{time.perf_counter() - started:.2f}s"
        )
        _cache_put(key, base)
        return base

    if allow_background:
        # Hand back the deterministic analysis now; the reader starts reading
        # while the model works. Same request, no extra round trip to see
        # something useful.
        base.refining = True
        base.refine_id = key
        _cache_put(key, base)
        if key not in _JOBS:
            _JOBS[key] = asyncio.create_task(_refine_job(key, text, language))
        print(
            f"[analyze] served heuristic in "
            f"{time.perf_counter() - started:.2f}s, refining in background"
        )
        return base

    return await _blocking_model_pass(key, text, prepared, started)
