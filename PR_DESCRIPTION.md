# Retrieval-grounded legal assistant, eight-language voice UI, and a legal toolkit

Open at: https://github.com/AmanDadsena/NyaySetu/pull/new/feat/rag-multilingual-voice

## Why

Three things were broken in ways that made the deployed app unusable, and none
of them were visible from the outside:

- The backend dropped and recreated every table on startup, so each restart
  deleted all users, cases and messages. This is why the lawyer directory was
  permanently empty.
- CORS declared a wildcard origin alongside `allow_credentials=True`. Browsers
  reject that combination outright, so no credentialed request could succeed.
- The Gemini key has **zero** free-tier quota — `429 RESOURCE_EXHAUSTED` with
  `limit: 0`. Every AI call was failing silently.

`backend/nyaysetu.db` was also tracked in git, publishing user records and
bcrypt hashes, and `JWT_SECRET_KEY` defaulted to a literal in this repository —
enough for anyone reading it to forge a token for any user id.

## What changed

### Answers come from statute, not a model's memory

Rather than paper over the dead API key, the dependency is inverted: retrieval
produces the law, generation only phrases it. Provider chain is
`ollama → gemini → extractive`, and the last path composes the reply from the
retrieved passages themselves — it cannot hallucinate a section number because
it never writes one.

82 curated passages, each carrying its act, section and a verifiable source.
BM25 over an inverted index (2ms at 20k passages), light stemming, a
cross-lingual legal lexicon, and optional multilingual embeddings.

**Retrieval is measured, not asserted.** `python -m app.rag.eval` scores 55
questions against expected passages plus four off-topic questions that must
return nothing:

| | before | after |
|---|---|---|
| hit@3 | 85.5% | **100%** |
| hit@1 | 76.4% | 85.5% |
| MRR | 0.800 | 0.918 |
| false positives | 3 / 4 | **0 / 4** |

The harness found two real bugs: no stemming (so "harassed" never matched
"harassment") and a relevance floor applied after normalisation, which made the
top result look confident even when nothing matched. Exits non-zero on
regression.

### Eight languages and voice

Locale resolved server-side from a cookie, so a Tamil visitor never sees a
frame of English. Dictation and read-aloud via the Web Speech API; asking by
voice reads the answer back automatically. Text is chunked on sentence
boundaries including the Devanagari danda, because Chromium stops after ~15s of
one utterance, and Markdown is stripped or the voice reads the asterisks.

### Legal toolkit

Deadline calculator (20 limitation periods), forum router (13 problem types),
and six document templates — RTI application and appeal, consumer notice,
Section 138 demand notice, SP escalation, legal notice. None of it calls a
model: lookup tables and calendar arithmetic, so it answers instantly, works
offline, and gives the same answer twice.

### Latency

Chat streams over SSE, sending citations before the first token: **0.22s to
first words** against a 26B local model, down from 33s.

### Other fixes

- Lawyer registration sent `specialties` as an array where the API expects a
  string — every attempt 422'd.
- No logged-in state anywhere; the navbar offered "Login" to signed-in users.
- Messages were escaped twice, so an apostrophe reached the user as `&#x27;`.
- Navigation was hidden below `md` with no replacement, leaving phone users
  unable to reach any page.
- Postgres support, so data survives a restart.

## Verification

- `python -m app.rag.eval` — passes, exits 0
- `npx tsc --noEmit` — clean
- `npm run build` — passes
- Auth, cases and messaging flows exercised end to end

## Not included

Billing and pricing. What makes this a SaaS is persistence and reliability, and
until `DATABASE_URL` points at Postgres in production, a restart still wipes
every account.

## Still needs action outside the code

- The Hugging Face Space is in an error state (`503`).
- The shared Vercel link sits behind Deployment Protection and redirects to a
  login page. The public URL is `nyay-setu-sigma.vercel.app`.
