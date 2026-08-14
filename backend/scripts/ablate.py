"""
Ablation study over the retrieval stack.

`app.rag.eval` answers "is it working". This answers "which part is doing the
work" — the question a reviewer asks and the one the eval alone cannot settle.
Every number the project claims about retrieval comes from a configuration with
four things switched on at once, and until you turn them off one at a time you
do not know whether the cross-lingual lexicon earns its 2,000 entries or the
embeddings earn their 470MB.

    python -m scripts.ablate                # every condition
    python -m scripts.ablate --curve        # corpus-size curve only
    python -m scripts.ablate --json out.json

Three studies:

  * **Components.** Lexicon and dense embeddings, on and off, in all four
    combinations. Scored on English and cross-lingual separately, because the
    components do not help both equally — that asymmetry is the finding.
  * **Corpus size.** Retrieval quality against the number of passages indexed,
    sampled deterministically so the curve is reproducible. Shows whether the
    corpus is near saturation or still paying for growth.
  * **Guards.** The out-of-corpus checks, measured as false-positive rate, so
    the cost of refusing to answer is visible next to the benefit.

Every run is deterministic: sampling is seeded, and the rank cutoffs match the
eval so the numbers can be quoted alongside it.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path
from typing import Callable

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import app.rag.retriever as retriever_module  # noqa: E402
from app.rag.corpus import CORPUS  # noqa: E402
from app.rag.eval import (  # noqa: E402
    CASES,
    MULTILINGUAL_CASES,
    NEAR_LAW_NEGATIVES,
    NEGATIVE_CASES,
    NEGATIVE_MULTILINGUAL,
)

#: Everyday off-topic questions in every language. The guard ablation is about
#: false positives, and counting only the English ones would understate what a
#: loosened semantic gate lets through.
ALL_NEGATIVES: list[str] = NEGATIVE_CASES + [q for _lang, q in NEGATIVE_MULTILINGUAL]

#: Reported alongside, never mixed in. These fail at every setting, so averaging
#: them into one rate would move a number that no guard controls and hide the
#: one that they do.
NEAR_LAW: list[str] = [q for _lang, q in NEAR_LAW_NEGATIVES]
from app.rag.retriever import Retriever  # noqa: E402

#: Sampling seed. Fixed so the corpus curve is the same on every machine.
SEED = 20260814


def _score(retriever: Retriever) -> dict[str, float]:
    """Run the full eval against one retriever configuration."""
    return _score_subset(retriever, CASES, MULTILINGUAL_CASES)


def _score_subset(
    retriever: Retriever,
    english: list[tuple[str, str]],
    multilingual: list[tuple[str, str, frozenset[str] | set[str]]],
) -> dict[str, float]:
    """
    Score one configuration over an explicit set of cases.

    Split out from `_score` so the corpus curve can restrict itself to the
    questions a smaller corpus could possibly answer.
    """
    hits1 = hits3 = 0
    rr = 0.0
    for question, expected in english:
        ids = [r.passage.id for r in retriever.search(question, top_k=3)]
        if ids[:1] == [expected]:
            hits1 += 1
        if expected in ids:
            hits3 += 1
            rr += 1.0 / (ids.index(expected) + 1)

    m1 = m3 = answered = 0
    for _lang, question, acceptable in multilingual:
        ids = [r.passage.id for r in retriever.search(question, top_k=3)]
        if ids:
            answered += 1
        if ids[:1] and ids[0] in acceptable:
            m1 += 1
        if acceptable & set(ids):
            m3 += 1

    false_positives = sum(1 for q in ALL_NEGATIVES if retriever.search(q, top_k=3))
    near_law = sum(1 for q in NEAR_LAW if retriever.search(q, top_k=3))

    n, m = max(len(english), 1), max(len(multilingual), 1)
    return {
        "en_hit1": hits1 / n,
        "en_hit3": hits3 / n,
        "en_mrr": rr / n,
        "ml_hit1": m1 / m,
        "ml_hit3": m3 / m,
        "ml_answered": answered / m,
        "fp_rate": false_positives / len(ALL_NEGATIVES),
        "near_law_rate": near_law / len(NEAR_LAW) if NEAR_LAW else 0.0,
    }


def _with_lexicon(enabled: bool) -> Callable[[], None]:
    """
    Swap the lexicon's expansion for a no-op.

    Patched at the retriever's reference rather than inside `lexicon.py`,
    because the retriever imported the function by name at module load.
    """
    original = retriever_module.expand

    def restore() -> None:
        retriever_module.expand = original

    if not enabled:
        retriever_module.expand = lambda tokens: tokens
    return restore


def _build(corpus: list, dense: bool, lexicon: bool) -> tuple[Retriever, Callable[[], None]]:
    restore = _with_lexicon(lexicon)
    if dense:
        r = Retriever(corpus, block_dense=True)
        if not r.dense.available:
            print("  [warn] dense requested but unavailable — install "
                  "sentence-transformers; reporting as BM25-only.")
    else:
        import os

        previous = os.environ.get("NYAYSETU_DISABLE_DENSE")
        os.environ["NYAYSETU_DISABLE_DENSE"] = "1"
        r = Retriever(corpus)
        if previous is None:
            del os.environ["NYAYSETU_DISABLE_DENSE"]
        else:
            os.environ["NYAYSETU_DISABLE_DENSE"] = previous
    return r, restore


_HEADER = (
    f"  {'condition':<26} {'en@1':>6} {'en@3':>6} {'MRR':>6} "
    f"{'ml@1':>6} {'ml@3':>6} {'ml ans':>7} {'FP':>5} {'nearlaw':>8}"
)


def _row(name: str, s: dict[str, float]) -> str:
    return (
        f"  {name:<26} {s['en_hit1']:>6.1%} {s['en_hit3']:>6.1%} {s['en_mrr']:>6.3f} "
        f"{s['ml_hit1']:>6.1%} {s['ml_hit3']:>6.1%} {s['ml_answered']:>7.1%} "
        f"{s['fp_rate']:>5.0%} {s['near_law_rate']:>8.0%}"
    )


def components() -> dict[str, dict[str, float]]:
    print("\n" + "=" * 78)
    print("COMPONENT ABLATION — which part of the stack is doing the work")
    print("=" * 78 + "\n")
    print(_HEADER)

    results: dict[str, dict[str, float]] = {}
    for lexicon in (False, True):
        for dense in (False, True):
            name = (
                f"{'BM25' if not dense else 'BM25+dense'}"
                f"{' +lexicon' if lexicon else ''}"
            )
            r, restore = _build(CORPUS, dense=dense, lexicon=lexicon)
            try:
                stats = _score(r)
            finally:
                restore()
            results[name] = stats
            print(_row(name, stats))
    print()
    return results


def corpus_curve(steps: int = 6) -> list[dict]:
    """
    Retrieval quality against corpus size.

    The obvious construction — keep every passage the eval names as an answer,
    sample the rest — produces a flat line here, because 125 of 149 passages
    are named answers and only 24 are free to vary. It measures nothing.

    So the whole corpus is sampled, and each step is scored only on the
    questions whose answer survived into that subset. That is the honest
    comparison: it asks whether a smaller corpus retrieves *its own* content as
    well, rather than punishing it for material it was never given. The count of
    scorable questions is reported alongside, since a percentage over 40
    questions and one over 122 are not the same claim.

    Sampling is seeded and nested — each step is a superset of the last — so the
    curve is reproducible and monotone in content.
    """
    print("\n" + "=" * 78)
    print("CORPUS SIZE CURVE — is the corpus saturated, or still paying?")
    print("=" * 78 + "\n")

    shuffled = list(CORPUS)
    random.Random(SEED).shuffle(shuffled)

    print("  Each step is scored only on the questions whose expected answer is")
    print("  present at that size, so smaller corpora are not marked down for")
    print("  passages they were never given.\n")
    print(f"  {'size':>12} {'en cases':>9} {'en@1':>6} {'en@3':>6} {'MRR':>6} "
          f"{'ml cases':>9} {'ml@1':>6} {'ml@3':>6} {'FP':>5}")

    rows: list[dict] = []
    for step in range(1, steps + 1):
        take = round(len(shuffled) * step / steps)
        subset = shuffled[:take]
        present = {p.id for p in subset}

        english = [(q, e) for q, e in CASES if e in present]
        multi = [
            (lang, q, acceptable & present)
            for lang, q, acceptable in MULTILINGUAL_CASES
            if acceptable & present
        ]

        r, restore = _build(subset, dense=False, lexicon=True)
        try:
            stats = _score_subset(r, english, multi)
        finally:
            restore()

        rows.append({"passages": len(subset), "en_cases": len(english),
                     "ml_cases": len(multi), **stats})
        print(f"  {len(subset):>9} psg {len(english):>9} {stats['en_hit1']:>6.1%} "
              f"{stats['en_hit3']:>6.1%} {stats['en_mrr']:>6.3f} {len(multi):>9} "
              f"{stats['ml_hit1']:>6.1%} {stats['ml_hit3']:>6.1%} "
              f"{stats['fp_rate']:>5.0%}")
    print()
    return rows


def guards() -> dict[str, dict[str, float]]:
    """
    What the out-of-corpus guards cost and buy.

    Both are measured by moving the floor rather than deleting the check, since
    the title rule only ever fires on queries the floor already admitted.
    """
    print("\n" + "=" * 78)
    print("GUARD ABLATION — the price of being able to say 'I don't know'")
    print("=" * 78 + "\n")
    print(_HEADER)

    original = retriever_module.MIN_ABSOLUTE_BM25
    results: dict[str, dict[str, float]] = {}
    try:
        for label, floor in [
            ("no floor (0.0)", 0.0),
            ("old floor (4.8)", 4.8),
            (f"shipped ({original})", original),
            ("aggressive (7.0)", 7.0),
        ]:
            retriever_module.MIN_ABSOLUTE_BM25 = floor
            r, restore = _build(CORPUS, dense=False, lexicon=True)
            try:
                stats = _score(r)
            finally:
                restore()
            results[label] = stats
            print(_row(label, stats))
    finally:
        retriever_module.MIN_ABSOLUTE_BM25 = original
    print()
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--curve", action="store_true", help="corpus-size curve only")
    parser.add_argument("--components", action="store_true", help="component ablation only")
    parser.add_argument("--guards", action="store_true", help="guard ablation only")
    parser.add_argument("--json", metavar="PATH", help="also write results as JSON")
    args = parser.parse_args()

    run_all = not (args.curve or args.components or args.guards)
    out: dict = {
        "corpus_size": len(CORPUS),
        "english_cases": len(CASES),
        "multilingual_cases": len(MULTILINGUAL_CASES),
        "negative_cases": len(NEGATIVE_CASES),
        "seed": SEED,
    }

    if run_all or args.components:
        out["components"] = components()
    if run_all or args.curve:
        out["corpus_curve"] = corpus_curve()
    if run_all or args.guards:
        out["guards"] = guards()

    if args.json:
        Path(args.json).write_text(json.dumps(out, indent=2), encoding="utf-8")
        print(f"Wrote {args.json}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
