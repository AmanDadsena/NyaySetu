# Nyaysetu — LinkedIn copy

Post `Nyaysetu-LinkedIn-Carousel.pdf` as a **document post**, not an image post.
An image post flattens all twelve slides into one picture and loses the swipe.

Document title: **How I built a legal assistant that can say "I don't know"**

---

## How to type the tags

A mention is not text. `@NALSA` pasted into the box stays grey and links to
nothing — LinkedIn only creates a mention when you type `@` in the composer and
choose an account from the dropdown it opens.

So the caption below ends with a **TAGS** line. Delete that whole line and type
the mentions yourself, one at a time:

1. Type `@` followed by the first few words — `@National Legal` — and pause.
2. Pick the organisation from the dropdown. The text turns into a blue link.
3. Repeat, separating each with a space.

If an account does not appear in the dropdown, it has no LinkedIn page. Delete
it rather than leaving dead text.

**Tag three to five, not fifteen.** A wall of mentions to organisations with no
connection to you reads as spam and LinkedIn's ranking treats it that way — it
can cost you reach rather than earn it.

### What to type, in order of how defensible the tag is

| Type this after `@` | Then pick | Why it is defensible |
|---|---|---|
| `National Legal Services` | National Legal Services Authority (NALSA) | The app routes people to free legal aid — NALSA's statutory job |
| `Department of Justice` | Department of Justice, Ministry of Law and Justice | Access-to-justice mandate |
| `MyGov India` | MyGov India | Citizen-facing digital public service |
| `Ministry of Law` | Ministry of Law and Justice, GoI | Owns the underlying legislation |
| `Startup India` | Startup India | Innovation angle, broad reach |

These are search terms, not confirmed handles — check each one resolves in the
dropdown before you rely on it.

**A named person beats an institution.** A legal-aid lawyer, a law professor, or
someone at a District Legal Services Authority will nearly always reply, where
an institutional page nearly always will not. One good individual tag is worth
more than all five above.

---

## SHORT VERSION — recommended

Most legal chatbots will confidently give you the wrong section number.

If you are checking whether you can still sue your landlord, a wrong answer is
not a worse answer. It is a harmful one.

So I built Nyaysetu the other way round: **retrieval produces the law, the model
only phrases it.** Every answer comes from 152 cited passages across 92 Indian
Acts. The model never writes a section number, because it never gets to invent
one.

What it does, free and without signup:

→ Ask a legal question in **8 Indian languages**, by text or voice
→ **Deadline calculator** — 20 limitation periods, court holidays included
→ **Where to file** — the right court, tribunal or authority for your problem
→ **Court fees**, stamp duty and maintenance estimates
→ **9 ready documents** — RTI, consumer notice, cheque bounce notice, and more
→ **Case plan** — one situation and one date give you the forum, every deadline,
the cost and the letter to send
→ Works **offline** once loaded

Measured, not claimed: 131 test questions, 92.4% top-1 accuracy, and 0 of 14
off-topic questions answered. It says "I don't know" on purpose.

Free legal aid is a statutory right for most people in India. Very few know it.

🔗 Try it: https://nyay-setu-sigma.vercel.app

TAGS — delete this line and type: @National Legal · @Department of Justice · @MyGov India

#LegalTech #AccessToJustice #AIforGood #India #RAG #OpenSource #LegalAid

---

## EVEN SHORTER — if the above still feels long

A legal assistant that answers only from cited Indian statute — and says
"I don't know" rather than guessing.

152 passages across 92 Acts. 8 Indian languages. Deadlines, court fees, the
right forum, and 9 ready-to-file documents. Free, no signup.

131 test questions → 92.4% top-1 accuracy, 0 of 14 off-topic questions answered.

Free legal aid is a statutory right for most Indians. Very few know it.

🔗 https://nyay-setu-sigma.vercel.app

TAGS — delete this line and type: @National Legal · @Department of Justice

#LegalTech #AccessToJustice #India #AIforGood #OpenSource

---

## Other accounts, if you want to swap any out

**Legal-tech peers — likelier to engage than a large firm**
SpotDraft · Provakil · Lawyered · Vakilsearch · LegalKart

**Large firms — low reply rate; use only with a real contact**
Cyril Amarchand Mangaldas · Khaitan & Co · Trilegal · AZB & Partners ·
Shardul Amarchand Mangaldas · Nishith Desai Associates

---

## Every figure above, and where it comes from

Checked against the live deployment, not recalled. Re-run before reposting if
the corpus has grown:

| Claim | Source |
|---|---|
| 152 passages, 92 Acts | `python -c "from app.rag.corpus import CORPUS; print(len(CORPUS))"` |
| 131 questions, 92.4%, 0/14 | `python -m app.rag.eval` |
| 20 limitation rules | `GET /api/tools/limitation` |
| 9 documents | `GET /api/tools/documents` |
| 13 forums, 13 situations | `GET /api/tools/forum`, `/api/tools/plan` |
| 8 languages | `src/lib/i18n/locales.ts` |

The carousel is rebuilt from `Nyaysetu-Carousel-Generator.py`, so the numbers in
the deck change in one place.
