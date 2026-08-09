"""
Retrieval evaluation.

This is the part of "training" that is actually defensible for this system.
There is no fine-tune to measure, but there *is* a retriever, and a retriever
can be scored: given a question a real user might ask, does the correct statute
come back, and does it come back first?

Run it:

    python -m app.rag.eval

Every question below names the passage that should be retrieved. Two metrics
are reported — hit@3 (is the right passage anywhere in the top three) and MRR
(how high it ranked). Both are standard for retrieval work, so the numbers mean
something to a reviewer.

Add a case whenever you add a passage. A corpus change that improves one topic
and quietly breaks another is otherwise invisible.
"""

from __future__ import annotations

import sys

from .retriever import get_retriever

#: (question, id of the passage that should be retrieved)
CASES: list[tuple[str, str]] = [
    # Police and criminal procedure
    ("What are my rights if the police arrest me?", "arrest_rights"),
    ("Police are refusing to file my FIR, what do I do?", "fir_refusal_remedy"),
    ("How do I register a first information report?", "fir_how_to_file"),
    ("The police say the crime happened in another area", "zero_fir"),
    ("Can I get bail before being arrested?", "anticipatory_bail"),
    ("Police have not filed a charge sheet in 90 days", "bail_default"),
    ("How do I complain about a police officer?", "police_complaint_against"),
    ("My child is missing, will police wait 24 hours?", "missing_person"),

    # Access to justice
    ("I cannot afford a lawyer, is there free legal help?", "legal_aid_eligibility"),
    ("Where do I apply for free legal aid?", "legal_aid_how_to_apply"),
    ("Can I settle my case without a full trial?", "lok_adalat"),

    # Constitution
    ("What are the fundamental rights in the Constitution?", "fundamental_rights"),
    ("What does the right to life cover?", "article_21"),
    ("How do I file a writ petition for habeas corpus?", "article_32"),
    ("Can Parliament amend any part of the Constitution?", "kesavananda"),
    ("Is privacy a fundamental right in India?", "puttaswamy"),
    ("What are the limits on freedom of speech?", "article_19_freedoms"),
    ("Is my child entitled to free schooling?", "article_21a_education"),
    ("What are the directive principles of state policy?", "directive_principles"),

    # Traffic
    ("What is the fine for drunk driving?", "mv_penalties_core"),
    ("How do I check and pay my e-challan?", "echallan_dispute"),
    ("What documents must I carry while driving?", "mv_documents_required"),
    ("How do I apply for a driving licence?", "mv_licence_how_to"),
    ("My son who is 16 was caught driving my car", "mv_juvenile_offence"),
    ("How do I claim compensation after a road accident?", "accident_compensation"),
    ("I sold my bike, do I need to transfer the RC?", "vehicle_transfer"),

    # Consumer and money
    ("Where do I file a consumer complaint?", "consumer_where_to_file"),
    ("An online seller refuses to refund me", "e_commerce_rights"),
    ("Money was taken from my bank account by fraud", "banking_fraud_liability"),
    ("My insurance claim was rejected", "insurance_claim_rejected"),
    ("Someone gave me a cheque that bounced", "cheque_bounce"),

    # Family and property
    ("What are the grounds for divorce?", "divorce_grounds_hindu"),
    ("We both want a divorce by mutual consent", "divorce_mutual_consent"),
    ("Can I claim maintenance from my husband?", "maintenance"),
    ("My husband is violent, what protection is there?", "domestic_violence"),
    ("Does a daughter have rights in ancestral property?", "daughters_coparcenary"),
    ("How do I claim my late father's bank balance?", "succession_certificate"),
    ("My son refuses to look after me, I gave him my house", "senior_citizens_maintenance"),

    # Work
    ("My employer has not paid my salary", "wage_theft"),
    ("Am I entitled to gratuity after five years?", "gratuity"),
    ("How much maternity leave am I entitled to?", "maternity_benefit"),
    ("Is my non-compete clause enforceable after I resign?", "contract_restraint"),
    ("I was harassed at work by my manager", "vishaka_posh"),

    # Cyber, data, other
    ("I was cheated in an online scam", "cybercrime_reporting"),
    ("Someone posted my private photos online", "obscene_content_online"),
    ("A man keeps following and messaging me", "bns_stalking"),
    ("What rights do I have over my personal data?", "data_protection"),
    ("How do I file an RTI application?", "rti_how_to_file"),
    ("My RTI was refused, can I appeal?", "rti_appeals"),
    ("My neighbours play loudspeakers at midnight", "noise_pollution"),
    ("What replaced the Indian Penal Code?", "bns_overview"),
    ("How long do I have to file a civil suit?", "limitation_periods"),
    ("Someone is spreading lies about me publicly", "defamation"),
    ("I have a disability, what reservation applies?", "disability_rights"),
    ("Am I entitled to subsidised ration?", "ration_food_security"),
]

#: Questions that are not about Indian law. The retriever should return nothing
#: rather than reaching for the closest passage — a confident wrong answer is
#: the worst outcome for a legal tool.
NEGATIVE_CASES: list[str] = [
    "What is the recipe for biryani?",
    "Who won the cricket world cup?",
    "How do I write a for loop in Python?",
    "What is the weather in Mumbai today?",
]


def run(verbose: bool = True) -> dict[str, float]:
    retriever = get_retriever()

    hits_at_1 = 0
    hits_at_3 = 0
    reciprocal_rank_total = 0.0
    misses: list[tuple[str, str, list[str]]] = []

    for question, expected in CASES:
        results = retriever.search(question, top_k=3)
        ids = [r.passage.id for r in results]

        if ids[:1] == [expected]:
            hits_at_1 += 1
        if expected in ids:
            hits_at_3 += 1
            reciprocal_rank_total += 1.0 / (ids.index(expected) + 1)
        else:
            misses.append((question, expected, ids))

    total = len(CASES)
    false_positives = [q for q in NEGATIVE_CASES if retriever.search(q, top_k=3)]

    metrics = {
        "cases": float(total),
        "hit@1": hits_at_1 / total,
        "hit@3": hits_at_3 / total,
        "mrr": reciprocal_rank_total / total,
        "false_positive_rate": len(false_positives) / len(NEGATIVE_CASES),
    }

    if verbose:
        print(f"\nRetrieval eval over {total} questions "
              f"({len(retriever.corpus)} passages, "
              f"dense={'on' if retriever.dense.available else 'off'})\n")
        print(f"  hit@1               {metrics['hit@1']:.1%}")
        print(f"  hit@3               {metrics['hit@3']:.1%}")
        print(f"  MRR                 {metrics['mrr']:.3f}")
        print(f"  false positives     {len(false_positives)}/{len(NEGATIVE_CASES)}")

        if misses:
            print(f"\n  {len(misses)} missed:")
            for question, expected, got in misses:
                print(f"    {question[:52]:54} want={expected}")
                print(f"      {'':52} got={got or '(nothing)'}")

        if false_positives:
            print("\n  Answered an out-of-scope question:")
            for question in false_positives:
                print(f"    {question}")
        print()

    return metrics


if __name__ == "__main__":
    results = run()
    # Non-zero exit on regression makes this usable as a CI gate.
    sys.exit(0 if results["hit@3"] >= 0.85 and results["false_positive_rate"] == 0 else 1)
