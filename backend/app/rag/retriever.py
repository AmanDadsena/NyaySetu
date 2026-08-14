"""
Hybrid retrieval over the legal corpus.

Two independent scorers, combined:

  * **BM25** — pure Python, no dependencies, always available. Strong on exact
    legal vocabulary: section numbers, act names, "anticipatory bail".
  * **Dense multilingual embeddings** — optional. If `sentence-transformers` is
    installed, a multilingual model handles a Hindi or Tamil question against
    the English corpus natively, which lexical matching cannot do.

Neither path calls a network service at query time, so retrieval keeps working
with no API key and no internet.
"""

from __future__ import annotations

import math
import os
import re
import threading
from dataclasses import dataclass

from .corpus import CORPUS, Passage
from .lexicon import expand

# Words that carry no retrieval signal in question-shaped queries.
STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "can", "do", "does", "for",
    "from", "get", "has", "have", "how", "i", "if", "in", "is", "it", "me", "my",
    "of", "on", "or", "should", "that", "the", "to", "was", "what", "when",
    "where", "which", "who", "will", "with", "you", "your", "am", "any", "about",
}

_TOKEN_RE = re.compile(r"[\wऀ-ॿ઀-૿஀-௿"
                       r"ఀ-౿ঀ-৿ಀ-೿]+", re.UNICODE)

#: Minimum raw BM25 score for a query to be considered in-corpus at all.
#:
#: Re-calibrated when the corpus grew from 82 to 137 passages, which shifted the
#: distribution enough that the previous floor of 4.8 began admitting "Tell me a
#: joke" and "What time does the mall open?".
#:
#: The margin here is genuinely narrow and worth understanding before changing
#: it. The binding constraint is not English prose but short questions in other
#: scripts: "ভোক্তা অভিযোগ কোথায়" is three words, expands to a single English
#: term through the lexicon, and scores 5.80 — while the highest-scoring
#: off-topic question that the title rule below does not already catch is "What
#: time does the mall open?" at 5.41. Everything rests in that gap. Raising this
#: to 6.0 silently stopped answering consumer questions in Tamil, Telugu,
#: Bengali and Kannada while every English metric stayed green, which is exactly
#: the failure the cross-lingual eval exists to catch.
MIN_ABSOLUTE_BM25 = float(os.environ.get("NYAYSETU_MIN_BM25", "5.5"))

#: How much of the blended score comes from BM25 rather than the embeddings,
#: when a dense index is present.
#:
#: Swept against the full eval rather than guessed, and the two halves of that
#: eval disagree — which is the whole reason the cross-lingual block exists.
#: Lowering this monotonically improves English and monotonically harms the
#: other seven languages:
#:
#:     weight   English hit@1   cross-lingual hit@1
#:     0.40         95.9%              76.8%
#:     0.65         94.3%              85.7%
#:     0.85         92.6%              91.1%
#:     1.00         91.8%              91.1%     (BM25 only)
#:
#: 0.85 is the point that beats BM25-only on English while costing the other
#: languages nothing. Going further trades roughly three points of Tamil,
#: Kannada and Bengali accuracy for one point of English, and an English speaker
#: asking about Indian law has alternatives that a Kannada speaker does not.
#: Cross-lingual hit@3 is 100% at every setting, so what moves here is which of
#: several relevant passages ranks first, not whether the law is found at all.
LEXICAL_WEIGHT = float(os.environ.get("NYAYSETU_LEXICAL_WEIGHT", "0.85"))

#: Minimum cosine similarity for the dense index alone to admit a query as
#: in-corpus, when there is no lexical evidence at all. Calibrated in the same
#: way as the BM25 floor and on the same eval: see `NEGATIVE_CASES`. This only
#: applies when sentence-transformers is installed; with BM25 alone it is unused.
MIN_DENSE_SIMILARITY = float(os.environ.get("NYAYSETU_MIN_DENSE", "0.45"))


#: Suffixes stripped to a common root, longest first so "-ations" is tried
#: before "-s". This is deliberately cruder than Porter: the corpus is small
#: and legal, and aggressive stemming collapses terms that must stay distinct
#: ("legal"/"legalise", "will"/"willing").
_SUFFIXES = (
    "ications", "ication", "ements", "ement", "ations", "ation", "ingly",
    "ments", "ment", "ness", "ings", "ing", "ies", "ied", "ers", "er",
    "ed", "es", "ly", "s",
)

#: Irregular or domain-specific pairs a suffix rule cannot reach. Without these
#: "harassed at work" never matches a passage about "harassment", and "my
#: husband is violent" never matches "domestic violence".
_STEM_OVERRIDES = {
    "harassed": "harass", "harassment": "harass", "harassing": "harass",
    "violent": "violen", "violence": "violen",
    "schooling": "school", "schools": "school",
    "lies": "lie", "lying": "lie",
    "children": "child", "child": "child",
    "women": "woman", "wives": "wife",
    "paid": "pay", "pays": "pay", "payment": "pay",
    "sold": "sell", "sells": "sell", "sale": "sell",
    "stolen": "steal", "theft": "steal",
    "driving": "drive", "drove": "drive", "driver": "drive",
    "complaint": "complain", "complaints": "complain",
    "inheritance": "inherit", "inherited": "inherit",
    "maintenance": "maintain", "maintaining": "maintain",
    "defamation": "defame", "defamatory": "defame",
    "minor": "minor", "juvenile": "minor",
    "fired": "terminate", "sacked": "terminate", "dismissal": "terminate",
}


def stem(token: str) -> str:
    """Reduce a token to a crude root so morphological variants match."""
    override = _STEM_OVERRIDES.get(token)
    if override:
        return override
    # Non-Latin scripts are left alone; Indic morphology does not respond to
    # English suffix rules and the lexicon handles those queries.
    if not token.isascii():
        return token
    for suffix in _SUFFIXES:
        if len(token) > len(suffix) + 2 and token.endswith(suffix):
            return token[: -len(suffix)]
    return token


def tokenize(text: str) -> list[str]:
    """Lowercase, stemmed word tokens. Indic scripts pass through intact."""
    return [
        stem(t)
        for t in (m.group(0).lower() for m in _TOKEN_RE.finditer(text))
        if t not in STOPWORDS and len(t) > 1
    ]


@dataclass
class RetrievedPassage:
    passage: Passage
    score: float
    #: Which scorers fired, for debugging and for the /sources response.
    matched_by: tuple[str, ...] = ()


class BM25:
    """
    Okapi BM25 backed by an inverted index.

    The obvious implementation loops over every document for every query. That
    is fine at a hundred passages and quietly becomes the bottleneck at twenty
    thousand, which is where this is heading once bare acts are ingested.

    Instead each term maps to a postings list of the documents containing it,
    so a query touches only documents that share a term with it — typically a
    small fraction of the corpus. Scoring is otherwise identical.
    """

    def __init__(self, documents: list[list[str]], k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.doc_count = len(documents)
        self.doc_lengths = [len(d) for d in documents]
        self.avg_doc_length = (
            sum(self.doc_lengths) / self.doc_count if self.doc_count else 0.0
        )

        # term -> [(doc index, term frequency), …]
        self.postings: dict[str, list[tuple[int, int]]] = {}
        for index, doc in enumerate(documents):
            frequencies: dict[str, int] = {}
            for term in doc:
                frequencies[term] = frequencies.get(term, 0) + 1
            for term, tf in frequencies.items():
                self.postings.setdefault(term, []).append((index, tf))

        # Standard BM25 idf, floored so that very common terms cannot go negative.
        self.idf = {
            term: max(
                0.05,
                math.log((self.doc_count - len(posting) + 0.5) / (len(posting) + 0.5) + 1.0),
            )
            for term, posting in self.postings.items()
        }

    def score(self, query_tokens: list[str]) -> dict[int, float]:
        """
        Score only the documents that share a term with the query.

        Returns a sparse mapping; documents absent from it scored zero. A query
        term repeated by lexicon expansion contributes once, matching the
        behaviour of the dense-loop version it replaced.
        """
        scores: dict[int, float] = {}
        for term in set(query_tokens):
            posting = self.postings.get(term)
            if not posting:
                continue
            idf = self.idf.get(term, 0.0)
            for index, tf in posting:
                length = self.doc_lengths[index]
                denominator = tf + self.k1 * (
                    1 - self.b + self.b * length / (self.avg_doc_length or 1)
                )
                scores[index] = scores.get(index, 0.0) + idf * (tf * (self.k1 + 1)) / denominator
        return scores


class _DenseIndex:
    """
    Optional multilingual embedding index.

    Never required: if sentence-transformers is missing, or the model cannot be
    fetched, retrieval silently continues on BM25 alone.

    Building happens on a background thread, which matters more than it sounds.
    The first call constructs a SentenceTransformer, and on a machine that has
    not cached the weights that means a ~470MB download — synchronous, and with
    no timeout worth relying on. Building inline made the *first user request*
    wait for it, so installing the library to improve retrieval would instead
    hang the first question someone asked. Now BM25 answers from the first
    moment and the dense half attaches when it is genuinely ready; `available`
    stays False until then, so every consumer degrades correctly by doing
    nothing differently.
    """

    MODEL_NAME = os.environ.get(
        "NYAYSETU_EMBED_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )

    def __init__(self) -> None:
        self.available = False
        self._model = None
        self._matrix = None

    #: How long a blocking build waits before giving up and letting the caller
    #: proceed on BM25. Long enough to cover a first-run model download on a
    #: reasonable connection, short enough that it cannot wedge a CI run.
    BUILD_TIMEOUT_SECONDS = float(os.environ.get("NYAYSETU_DENSE_TIMEOUT", "300"))

    def build(self, texts: list[str], block: bool = False) -> None:
        """
        Start building. Returns immediately unless `block` is set, which the
        eval harness uses so a run measures the retrieval it means to measure
        rather than whatever happened to be loaded when it started.

        Even a blocking build is bounded. The first one may have to download the
        weights, and on a slow link that is minutes — long enough that an
        unbounded wait turns "run the eval" into an apparent hang with no output
        to explain it.
        """
        if os.environ.get("NYAYSETU_DISABLE_DENSE") == "1":
            print("[rag] Dense retrieval disabled by environment.")
            return
        try:
            from sentence_transformers import SentenceTransformer  # noqa: F401
        except ImportError:
            print("[rag] sentence-transformers not installed — BM25 only. "
                  "Install it to enable cross-lingual semantic search.")
            return

        thread = threading.Thread(
            target=self._build_now, args=(texts,), name="dense-index", daemon=True
        )
        thread.start()

        if not block:
            return

        thread.join(self.BUILD_TIMEOUT_SECONDS)
        if thread.is_alive():
            print(f"[rag] Dense index still building after "
                  f"{self.BUILD_TIMEOUT_SECONDS:.0f}s (first run downloads the "
                  f"model). Continuing on BM25; re-run once it has cached.")

    def _build_now(self, texts: list[str]) -> None:
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore

            model = SentenceTransformer(self.MODEL_NAME)
            matrix = model.encode(
                texts, normalize_embeddings=True, show_progress_bar=False
            )
            # Publish both halves before flipping the flag, so a concurrent
            # search never sees a model with no matrix to score against.
            self._model = model
            self._matrix = matrix
            self.available = True
            print(f"[rag] Dense index ready ({self.MODEL_NAME}).")
        except Exception as exc:  # model download / runtime failure
            print(f"[rag] Dense index unavailable ({exc}). Continuing with BM25.")

    def score(self, query: str) -> list[float] | None:
        if not self.available or self._model is None or self._matrix is None:
            return None
        try:
            vector = self._model.encode([query], normalize_embeddings=True)[0]
            return (self._matrix @ vector).tolist()
        except Exception:
            return None


class Retriever:
    def __init__(self, corpus: list[Passage], block_dense: bool = False):
        self.corpus = corpus

        # Index the searchable surface of each passage. Title, topics and the
        # former section numbers are repeated so a query naming one of them
        # outranks a passage that merely mentions the words in passing.
        self.documents: list[list[str]] = []
        self.plain_texts: list[str] = []
        #: Tokens from the passage's own name — what it is *about*, as opposed to
        #: every word that happens to appear in it. Used to sanity-check a match
        #: that rests on a single query term; see `search`.
        self.label_tokens: list[set[str]] = []
        for passage in corpus:
            searchable = " ".join(
                [
                    passage.title, passage.title,
                    passage.act,
                    passage.section, passage.section,
                    " ".join(passage.topics), " ".join(passage.topics),
                    " ".join(passage.also_known_as), " ".join(passage.also_known_as),
                    passage.text,
                ]
            )
            self.documents.append(tokenize(searchable))
            self.plain_texts.append(f"{passage.title}. {passage.text}")
            self.label_tokens.append(
                set(tokenize(passage.title + " " + " ".join(passage.also_known_as)))
            )

        self.bm25 = BM25(self.documents)
        self.dense = _DenseIndex()
        self.dense.build(self.plain_texts, block=block_dense)

    def search(self, query: str, top_k: int = 4, min_score: float = 0.18) -> list[RetrievedPassage]:
        """
        Return the best passages for a query, normalised to a 0–1 score.

        `min_score` is a relevance floor: below it the engine treats the query
        as out of corpus and says so, rather than answering from a weak match.
        """
        tokens = expand(tokenize(query))
        if not tokens:
            return []

        sparse = self.bm25.score(tokens)
        lexical_max = max(sparse.values()) if sparse else 0.0
        semantic = self.dense.score(query)

        # ── Is this question in the corpus at all? ──────────────────────
        #
        # Being able to say "I don't know" is the single most important
        # behaviour for a legal tool, and it has to hold in both retrieval
        # modes. An earlier version switched both guards off whenever a dense
        # index was present, on the reasoning that embeddings would sort it out;
        # what that actually did was remove every out-of-corpus check on exactly
        # the deployments that have the most ways to produce a confident-looking
        # wrong match. The evidence tests below are therefore evaluated
        # independently and either one can admit a query.
        #
        # Lexical evidence: a real BM25 score, applied *before* normalisation.
        # Normalising makes the best match 1.0 whether it scored 14 or 0.9, so a
        # question about cricket otherwise produces a confident top result.
        lexical_evidence = lexical_max >= MIN_ABSOLUTE_BM25

        # ...but a match resting on a single query word is only believable when
        # that word is what the passage is called. "Someone gave me a cheque
        # that bounced" matches one term, and that term is the title of the
        # cheque passage, so it is a real hit. "The best pizza in town" also
        # matches one term — "town", from "Town Vending Committee" buried in the
        # body of the street-vending passage — and scores *higher*, because
        # rarity in a small corpus is not relevance. No score threshold
        # separates those two; asking where the word appears does.
        if lexical_evidence and sparse:
            best = max(sparse, key=lambda i: sparse[i])
            matched = set(tokens) & set(self.documents[best])
            if len(matched) == 1 and not (matched & self.label_tokens[best]):
                lexical_evidence = False

        # Semantic evidence: a genuine embedding match. This is what lets a
        # question phrased in words the corpus never uses still land, and it is
        # the only route for a language the lexicon does not cover.
        semantic_evidence = (
            semantic is not None and max(semantic, default=0.0) >= MIN_DENSE_SIMILARITY
        )

        if not lexical_evidence and not semantic_evidence:
            return []

        # Only documents with some lexical signal are candidates, unless a dense
        # index is present — a semantic match on a document sharing no vocabulary
        # with the query is exactly what embeddings are for.
        if semantic is not None:
            candidates = set(sparse) | {
                i for i, s in enumerate(semantic) if s >= 0.30
            }
        else:
            candidates = set(sparse)

        if not candidates:
            return []

        # With no lexical signal anywhere, the blend has nothing to blend: every
        # `lex` is zero, so a weighted score collapses to (1 - weight) x sem and
        # can never clear `min_score`. At a lexical weight of 0.85 that silently
        # closed the semantic-only route entirely — the very path embeddings are
        # installed for. Rank on the semantic score directly instead; the
        # weighting only means something when both signals are present.
        semantic_only = lexical_max <= 0.0 and semantic is not None

        scored: dict[int, tuple[float, float, float]] = {}
        for index in candidates:
            lex = (sparse.get(index, 0.0) / lexical_max) if lexical_max > 0 else 0.0
            if semantic is not None:
                # Cosine similarity of a normalised multilingual model sits
                # roughly in 0.0–0.8 for relevant pairs; rescale before blending.
                sem = max(0.0, min(1.0, semantic[index] / 0.75))
                combined = sem if semantic_only else (
                    LEXICAL_WEIGHT * lex + (1.0 - LEXICAL_WEIGHT) * sem
                )
            else:
                sem = 0.0
                combined = lex
            scored[index] = (combined, lex, sem)

        # An absolute floor alone is not enough. Scores are normalised against
        # the best match, so on any query the runners-up sit at some fraction
        # of 1.0 whether or not they are relevant — which is how a question
        # about a landlord ends up citing the Food Security Act. Requiring a
        # result to be in the same league as the winner cuts that off.
        top = max(c for c, _, _ in scored.values())
        floor = max(min_score, top * 0.62)

        ranked: list[RetrievedPassage] = []
        for index, (combined, lex, sem) in scored.items():
            if combined < floor:
                continue
            matched: list[str] = []
            if lex > 0.15:
                matched.append("keyword")
            if semantic is not None and sem > 0.35:
                matched.append("semantic")
            ranked.append(
                RetrievedPassage(
                    passage=self.corpus[index],
                    score=round(combined, 4),
                    matched_by=tuple(matched),
                )
            )

        # Ties are broken by corpus order so results are stable between runs.
        ranked.sort(key=lambda r: (-r.score, r.passage.id))
        return ranked[:top_k]


_retriever: Retriever | None = None
_lock = threading.Lock()


def get_retriever(block_dense: bool = False) -> Retriever:
    """
    Build the index once per process, on first use.

    `block_dense` waits for the embedding index before returning. Serving never
    wants this — BM25 is ready immediately and dense attaches when it can — but
    the eval does, because a run that started before the embeddings finished
    would report BM25 numbers under a dense heading.
    """
    global _retriever
    if _retriever is None:
        with _lock:
            if _retriever is None:
                _retriever = Retriever(CORPUS, block_dense=block_dense)
    return _retriever
