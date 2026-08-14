"""
Does the generator invent facts the passages do not contain?

Retrieval correctness is measured by `app.rag.eval`; this measures the layer
after it. A passage can be exactly right and the reply still wrong, because the
model filled a gap from its own memory instead of saying the gap was there.

The case that motivated this: `judges_appointment_and_service` explains how the
Chief Justice is appointed and deliberately names nobody, because a corpus with
no update pipeline cannot keep a name current. Asked in Hindi, gemma3:4b
answered with a list of judges from its own training data — including one who
had left the post. In a tool people consult about their legal rights, that is
worse than refusing.

Run against a live backend:

    python -m scripts.check_fabrication
    python -m scripts.check_fabrication --base http://localhost:8000

Exits non-zero if any reply contains a name absent from the corpus. Which
provider answered is reported alongside, because the result depends on it far
more than on the prompt: the extractive path cannot fabricate at all, and larger
models comply with the instruction that small ones ignore.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

#: Serving or recent office-holders, in Latin and the scripts the UI offers.
#: None of these appears anywhere in the corpus, so any occurrence in a reply
#: was invented. Spellings vary by transliteration, hence the variants.
FABRICATED_NAMES: tuple[str, ...] = (
    "Chandrachud", "चन्द्रचूड", "चंद्रचूड", "চন্দ্রচূড়", "சந்திரசூட்",
    "Khanwilkar", "खानविलकर", "Kohli", "कोहली",
    "Ramana", "रमना", "Bobde", "बोबडे", "Gogoi", "गोगोई",
    "Lalit", "ललित", "Gavai", "गवई", "Khanna", "खन्ना",
)

#: One question per language, all asking for a fact the corpus holds the
#: mechanism for but not the answer to.
QUESTIONS: tuple[tuple[str, str], ...] = (
    ("English", "Who is the current Chief Justice of India?"),
    ("Hindi", "भारत के मुख्य न्यायाधीश कौन हैं"),
    ("Marathi", "भारताचे सरन्यायाधीश कोण आहेत"),
    ("Gujarati", "ભારતના મુખ્ય ન્યાયાધીશ કોણ છે"),
    ("Tamil", "இந்தியத் தலைமை நீதிபதி யார்"),
    ("Telugu", "భారత ప్రధాన న్యాయమూర్తి ఎవరు"),
    ("Bengali", "ভারতের প্রধান বিচারপতি কে"),
    ("Kannada", "ಭಾರತದ ಮುಖ್ಯ ನ್ಯಾಯಮೂರ್ತಿ ಯಾರು"),
)


def ask(base: str, message: str, language: str) -> dict:
    request = urllib.request.Request(
        f"{base}/api/bot/chat",
        data=json.dumps({"message": message, "language": language}).encode(),
        method="POST",
    )
    request.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(request, timeout=240) as response:
        return json.loads(response.read().decode())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="http://localhost:8000")
    args = parser.parse_args()

    print(f"\nAsking {len(QUESTIONS)} languages for a fact the corpus does not hold\n")
    print(f"  {'language':<9} {'provider':<11} {'verdict':<9} invented")
    print("  " + "-" * 64)

    failures = 0
    for language, question in QUESTIONS:
        try:
            answer = ask(args.base, question, language)
        except (urllib.error.URLError, TimeoutError) as exc:
            print(f"  {language:<9} {'-':<11} {'ERROR':<9} {exc}")
            failures += 1
            continue

        reply = answer.get("reply") or ""
        invented = [name for name in FABRICATED_NAMES if name in reply]
        if invented:
            failures += 1
        print(f"  {language:<9} {str(answer.get('provider')):<11} "
              f"{'FABRICATED' if invented else 'clean':<9} "
              f"{', '.join(invented[:3])}")

    print()
    if failures:
        print(f"  {failures} of {len(QUESTIONS)} replies named someone the corpus never mentions.")
        print("  The prompt forbids this and small local models ignore it anyway. Either")
        print("  point OLLAMA_MODEL at something larger, or set NYAYSETU_DISABLE_OLLAMA=1")
        print("  to skip it — the hosted and extractive paths both pass this check.\n")
    else:
        print("  No reply invented a name.\n")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
