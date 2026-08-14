# Retrieval-grounded legal assistant, eight languages, and a toolkit that answers the whole question

Open at: https://github.com/AmanDadsena/NyaySetu/compare/main...feat/rag-multilingual-voice

## Why

Three things were broken in ways that were invisible from the outside:

- The backend dropped and recreated every table on startup, so each restart
  deleted all users, cases and messages. This is why the lawyer directory was
  permanently empty.
- CORS declared a wildcard origin alongside `allow_credentials=True`. Browsers
  reject that combination outright, so no credentialed request could succeed.
- Every AI call failed. The cause was misdiagnosed for a long time as a dead
  API key; it was actually a decommissioned model name returning `404`.

`backend/nyaysetu.db` was also tracked in git, publishing user records and
bcrypt hashes, and `JWT_SECRET_KEY` defaulted to a literal in this repository —
enough for anyone reading it to forge a token for any user id.

## Answers come from statute, not a model's memory

The dependency is inverted: retrieval produces the law, generation only phrases
it. The provider chain is `ollama → gemini → extractive`, and the last path
composes the reply from the retrieved passages themselves — it cannot invent a
section number because it never writes one.

**152 curated passages**, each carrying its act, its section and a verifiable
source. Hybrid retrieval: BM25 over an inverted index, a cross-lingual legal
lexicon of 2,012 entries, and multilingual embeddings fused by reciprocal rank.

### Retrieval is measured, not asserted

`python -m app.rag.eval` is the gate. It did not exist on `main`.

| | result |
|---|---|
| questions | 131 |
| hit@1 | 92.4% |
| hit@3 | 100% |
| MRR | 0.961 |
| false positives | 0 / 14 |

It reports cross-lingual scores **separately**, because an aggregate dominated
by English hides the failure completely — 70 questions across seven languages,
100% answered, 93% hit@1, 100% hit@3. That block caught two regressions nothing
else would have: Hindi returning empty for a landlord question, and a stricter
BM25 floor silently killing consumer questions in Tamil, Telugu, Bengali and
Kannada while every English metric stayed green.

`scripts/ablate.py` answers which part of the stack does the work:

| condition | English hit@1 | cross-lingual hit@1 |
|---|---|---|
| BM25 | 91.5% | 0% |
| BM25 + dense | 92.3% | 50.7% |
| BM25 + lexicon | 91.5% | 88.1% |
| **all three** | **92.3%** | **92.5%** |

English retrieval saturates around 74 passages; cross-lingual keeps improving
to 152, which is the argument for growing the corpus rather than tuning it.

Two bugs came out of building that harness. The lexicon and the dense index had
both been scoring against an eval that only measured English. And the two
scorers were never on the same scale — BM25 was normalised against the best
match while cosine was absolute, so a weighted mean guaranteed the top lexical
hit at least 0.85 and capped an embeddings-only match at 0.15, below the
relevance floor. The dense index could reorder passages that already shared
vocabulary with the query and could never introduce one that did not.

## Saying "I don't know"

The most important behaviour for a legal tool, and it needs its own tests.

A larger corpus offers more incidental words to match on: "the best pizza in
town" retrieved street-vending law via "Town Vending Committee", scoring
*higher* than a legitimate one-word match on "cheque". No threshold separates
those, so a single-term match is only believed when that term appears in the
passage title. Guard ablation: no floor gives 13% false positives, the shipped
floor 0%, and an aggressive floor buys nothing while costing 11 points of
cross-lingual recall.

Generation is checked too. `scripts/check_fabrication.py` asks all eight
languages for a fact the corpus deliberately does not hold — who currently
holds an office the passages only describe — and fails if any reply names
someone. `gemma3:4b` fabricates in 1 of 8; the hosted and extractive paths in
0 of 8. `NYAYSETU_DISABLE_OLLAMA=1` is set in both production configs for that
reason, not for latency.

## Eight languages

Locale resolved server-side from a cookie, so a Tamil visitor never sees a frame
of English. 96 UI keys, complete across all eight locales. Dictation and
read-aloud via the Web Speech API; asking by voice reads the answer back. Text
is chunked on sentence boundaries including the Devanagari danda, because
Chromium stops after ~15s of one utterance.

Generated replies are verified to be in the script that was asked for and fall
through to another provider otherwise, because small models follow a language
instruction unreliably.

## A toolkit that answers the question people arrive with

Nobody wants a limitation period; they want to know what to do about their
landlord. **One situation and one date** produce the forum, every deadline in
the order they fall, the cost, what to gather, the letter to send first, and
what happens after filing — composed from the existing calculators rather than
reimplementing them, so the plan can never disagree with the tool it came from.
Thirteen situations.

Behind it: 20 limitation rules with Section 4 resolved against a real court
calendar, 13 forum routes, 9 document templates, court fees, stamp duty,
maintenance ranges, and a citation extractor. None of it calls a model.

The lookup tables are also served to the browser and the arithmetic repeated
there, so the deadline calculator works with no network.
`scripts/check_offline_parity.py` runs every rule through both implementations
across leap days, month ends and holidays — 160 cases, 11 fields each, and
fails if they ever disagree.

## Finding out where the corpus is thin

Users who get a bad answer rarely complain; they rephrase and try again. That
retry is recorded as a miss against the first question, and `scripts/gaps.py`
ranks what to fix.

Off unless `NYAYSETU_FEEDBACK_LOG` is set. No user id, account or IP. The
session key groups two requests and maps to nothing. Question text is stored
only under a second flag, and the log is gitignored — these are people's legal
problems.

## Other fixes

- Lawyer registration sent `specialties` as an array where the API expects a
  string — every attempt 422'd.
- No logged-in state anywhere; the navbar offered "Login" to signed-in users.
- Messages were escaped twice, so an apostrophe reached the user as `&#x27;`.
- Navigation was hidden below `md` with no replacement, leaving phone users
  unable to reach any page.
- Postgres support, so data survives a restart.
- Pressing a toolkit action while signed out now goes to the sign-in page
  carrying `next`, and the page says what it was for.

## Verification

- `python -m app.rag.eval` — passes, exits 0
- `python -m scripts.ablate` — component, corpus-size and guard ablations
- `python scripts/check_offline_parity.py` — 160/160 agree
- `python -m scripts.check_fabrication` — 0/8 with the shipped config
- `npx tsc --noEmit` — clean
- `npm run build` — passes
- Auth, cases, messaging, toolkit and analyze exercised end to end

## Known limitations

- Three questions about police recruitment dates are answered when they should
  be refused. They are State-specific and change every cycle; nothing here
  claims to track them. Tracked in `NEAR_LAW_NEGATIVES`, reported by the eval,
  deliberately not gating the build.
- The dense-only path answers 86% of cross-lingual questions rather than all of
  them, limited by `MIN_DENSE_SIMILARITY`. The lexicon covers the shortfall for
  the eight languages shipped; a ninth would need lexicon entries.
- Billing and pricing are not included.

## Still needs action outside the code

- Set `GEMINI_API_KEY` and `DATABASE_URL` in the Render dashboard. Until
  `DATABASE_URL` points at Postgres, a restart still wipes every account.
- The Hugging Face Space is in an error state (`503`).
- The shared Vercel link sits behind Deployment Protection and redirects to a
  login page. The public URL is `nyay-setu-sigma.vercel.app`.
