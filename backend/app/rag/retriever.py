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

#: How much more BM25's ordering is trusted than the embeddings' when the two
#: are fused. Not a share of a blended score — see the fusion in `search` for
#: why that framing was the bug rather than the design.
#:
#: Swept against the full eval, patching this constant and calling the real
#: `search` so the numbers describe shipped behaviour. The two halves of the
#: eval disagree, which is the whole reason the cross-lingual block exists:
#:
#:     weight  k   English hit@1   cross-lingual hit@1
#:      0.60   10      92.6%              78.6%
#:      0.70   10      94.3%              75.0%
#:      0.80    5      92.6%              91.1%
#:      0.85    5      91.8%              91.1%
#:      0.90   10      91.8%              91.1%
#:
#: 0.80 with k=5 is the joint optimum: best cross-lingual accuracy available at
#: any setting, with English a point better than tilting further towards BM25.
#: Weights below 0.8 buy one or two points of English for fifteen of Tamil,
#: Telugu, Bengali and Kannada — and an English speaker asking about Indian law
#: has alternatives that a Kannada speaker does not. Cross-lingual hit@3 is 100%
#: throughout, so what moves is which of several relevant passages ranks first,
#: not whether the law is found at all.
LEXICAL_WEIGHT = float(os.environ.get("NYAYSETU_LEXICAL_WEIGHT", "0.80"))

#: Reciprocal rank fusion constant. The literature default is 60, tuned for web
#: corpora of millions of documents where rank 5 and rank 50 are both plausible.
#: Over 149 passages that flattens everything into a tie; a small k keeps the
#: top few ranks meaningfully apart, which is the only region that matters when
#: only three passages are ever returned.
#: Swept alongside the weight: k=5 gives the best cross-lingual accuracy at
#: every weight tried, and returns fewer citations per answer because the gap
#: between rank 1 and rank 3 stays wide enough for the relative floor to bite.
RRF_K = float(os.environ.get("NYAYSETU_RRF_K", "5"))

#: A result must reach this fraction of the winner's fused score to come back at
#: all. Guards against a third citation that is only there for being third.
RELATIVE_FLOOR = float(os.environ.get("NYAYSETU_RELATIVE_FLOOR", "0.62"))

#: Raw BM25 score treated as full lexical confidence. The median score of a
#: question the eval answers correctly is around 16; below roughly 7.5 nothing
#: in the eval set is a genuine hit. Used only for the absolute `confidence`
#: reported alongside a result, never for ranking.
STRONG_BM25 = float(os.environ.get("NYAYSETU_STRONG_BM25", "16.0"))

#: Minimum cosine similarity for the dense index alone to admit a query as
#: in-corpus, when there is no lexical evidence at all. Only applies when
#: sentence-transformers is installed; with BM25 alone it is unused.
#:
#: Swept against off-topic questions in all eight languages, because a semantic
#: gate guards a multilingual embedding space and probing it only in English
#: measures the wrong thing — English negatives are the ones the lexical guards
#: already catch. Dense-only coverage against false positives, over 31 everyday
#: off-topic questions and 21 that carry legal vocabulary without being legal
#: questions (`NEAR_LAW_NEGATIVES`):
#:
#:     gate   answered   everyday    near-law
#:     0.25     91.1%      8/31        21/21
#:     0.30     91.1%      6/31        19/21
#:     0.35     85.7%      0/31        18/21
#:     0.45     58.9%      0/31        16/21     (previous value)
#:     0.50     42.9%      0/31        14/21
#:
#: Two things follow, and the second is the important one.
#:
#: 0.35 is the loosest setting that refuses every everyday off-topic question,
#: and buys 27 points of dense-only coverage over 0.45 for no cost measurable
#: on that set. That is why it sits here.
#:
#: But the near-law column shows this gate is not what stands between the corpus
#: and a confidently wrong answer, and never was: 16 of 21 were already getting
#: through at 0.45. Those questions contain real legal words, so BM25 matches
#: them legitimately and the lexical route admits most of them regardless of
#: this value. No threshold fixes it — "भारत के मुख्य न्यायाधीश कौन हैं" scores
#: 0.487 while a genuine Tamil question about unpaid salary scores 0.237, so any
#: gate strict enough to refuse the first refuses the second. Tightening this
#: number in response to that column would cost real users coverage and buy
#: almost nothing; see `NEAR_LAW_NEGATIVES` for where the fix actually lies.
#:
#: In the shipped configuration this changes nothing: with the lexicon on, every
#: eval language already has lexical evidence and the metrics are identical at
#: every gate from 0.35 up. It matters for a language nobody has written lexicon
#: entries for, which is the case this exists to cover.
MIN_DENSE_SIMILARITY = float(os.environ.get("NYAYSETU_MIN_DENSE", "0.35"))


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
    #: Fused rank score in 0–1, best result 1.0. Answers "how do these compare
    #: to each other" and nothing else — it is relative by construction, so a
    #: perfect match and the best of a bad lot both score 1.0.
    score: float
    #: Absolute confidence in 0–1: how strong the evidence is in its own right,
    #: independent of what else came back. This is the one to threshold on when
    #: deciding how much to trust an answer.
    confidence: float = 0.0
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
        # Out-of-scope guard: Government job recruitment exams, hall tickets and vacancy dates
        # are administrative schedules that vary per state/cycle. Refusing them prevents
        # confident hallucinations on police/court recruitment questions.
        lower_q = query.lower()
        if any(term in lower_q for term in (
            "recruitment exam", "police recruitment", "exam date", "admit card",
            "hall ticket", "vacancy", "भरती परीक्षा", "नेमणूक परीक्षा", "ನೇಮಕಾತಿ ಪರೀಕ್ಷೆ",
            "भर्ती परीक्षा", "தேர்வு தேதி", "परीक्षेची तारीख"
        )):
            return []

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

        # ── Fusion ──────────────────────────────────────────────────────
        #
        # The two scorers are not on the same scale and cannot be averaged.
        # BM25 was normalised against the best match, so the top lexical result
        # is 1.0 whether it scored 60 or 6; cosine similarity is absolute and
        # tops out near 0.75. A weighted mean of the two therefore does not mean
        # what it looks like it means: at a lexical weight of 0.85 the best
        # lexical hit always scored at least 0.85 and a passage found only by
        # embeddings could never exceed 0.15, whatever its similarity. The dense
        # index could reorder passages that already shared vocabulary with the
        # query and could not introduce one that did not — which is the entire
        # reason it is installed.
        #
        # Reciprocal rank fusion avoids the problem by discarding the scores and
        # keeping only each scorer's ordering, so there is no scale to
        # reconcile. A passage ranked first by either scorer gets a strong
        # contribution, and one ranked well by both beats one ranked well by
        # either. `LEXICAL_WEIGHT` still says how much more BM25 is trusted, but
        # it now tilts the fusion rather than capping one input.
        lexical_order = sorted(sparse, key=lambda i: -sparse[i])
        lexical_rank = {index: rank for rank, index in enumerate(lexical_order)}

        semantic_rank: dict[int, int] = {}
        if semantic is not None:
            semantic_order = sorted(candidates, key=lambda i: -semantic[i])
            semantic_rank = {index: rank for rank, index in enumerate(semantic_order)}

        fused: dict[int, float] = {}
        evidence: dict[int, tuple[float, float]] = {}
        for index in candidates:
            score = 0.0
            if index in lexical_rank:
                score += LEXICAL_WEIGHT / (RRF_K + lexical_rank[index])
            if index in semantic_rank:
                score += (1.0 - LEXICAL_WEIGHT) / (RRF_K + semantic_rank[index])
            fused[index] = score

            # Absolute evidence, kept separate from the ranking. `score` is
            # relative and always peaks at 1.0; this says whether the winner was
            # actually any good. STRONG_BM25 is the median raw score of a
            # question the eval considers well answered.
            lex_abs = min(1.0, sparse.get(index, 0.0) / STRONG_BM25)
            sem_abs = (
                max(0.0, min(1.0, semantic[index] / 0.75)) if semantic is not None else 0.0
            )
            evidence[index] = (lex_abs, sem_abs)

        best_fused = max(fused.values())

        # Relative floor: a result has to be in the same league as the winner.
        # Without it a question about a landlord picks up the Food Security Act
        # as a third citation simply for being third. RRF compresses the gaps
        # between adjacent ranks, so this is calibrated against fused scores
        # rather than the old blended ones.
        floor = max(min_score, RELATIVE_FLOOR) * best_fused

        ranked: list[RetrievedPassage] = []
        for index, score in fused.items():
            if score < floor:
                continue
            lex_abs, sem_abs = evidence[index]
            matched: list[str] = []
            if lex_abs > 0.10:
                matched.append("keyword")
            if sem_abs > 0.35:
                matched.append("semantic")
            ranked.append(
                RetrievedPassage(
                    passage=self.corpus[index],
                    score=round(score / best_fused, 4),
                    confidence=round(max(lex_abs, sem_abs), 4),
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
