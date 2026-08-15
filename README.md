---
title: Nyaysetu Backend
emoji: 🌖
colorFrom: indigo
colorTo: gray
sdk: docker
pinned: false
---

# Nyaysetu

A legal-information assistant for India that answers from cited statute rather
than from a model's memory, in eight languages, with a toolkit for the things
people otherwise pay someone to work out: the deadline, the right forum, the
paperwork, and what it all costs.

Next.js frontend, FastAPI backend.

---

## How it answers

The dependency most systems take on a language model is inverted here.
**Retrieval produces the law; generation only phrases it.** Providers are tried
in order — a local model via Ollama, then a hosted model, then an extractive
answer composed from the retrieved passages themselves. The last path needs no
key, no quota and no network, and it cannot invent a section number because it
never writes one.

The corpus is **152 curated passages across 92 Acts**, each carrying its act,
its section and a verifiable source. Retrieval is hybrid:

- **BM25** over an inverted index — strong on exact legal vocabulary.
- **A cross-lingual lexicon** of 2,009 entries mapping legal terms in seven
  Indian languages onto the English the corpus uses, with prefix and stem
  matching so inflected forms still land.
- **Multilingual embeddings**, optional, fused with BM25 by reciprocal rank.

Deciding a question is out of corpus is treated as a feature, not a failure.
Several guards have to agree before an answer is produced at all, because a
confident wrong answer is the worst outcome for a legal tool.

## Measured, not asserted

`python -m app.rag.eval` is the gate for any change to the corpus, the lexicon
or the retriever. It exits non-zero on regression.

| | |
|---|---|
| questions | 131 |
| hit@1 | 92.4% |
| hit@3 | 100% |
| MRR | 0.961 |
| false positives | 0 / 14 |

Cross-lingual results are scored **separately**, because an aggregate dominated
by English hides the failure completely: 70 questions across seven languages,
100% answered, 93% hit@1, 100% hit@3. That block has caught regressions that
every English metric stayed green through.

---

## The toolkit

None of it calls a model. Lookup tables and calendar arithmetic, so answers are
instant, identical every time, and cite the provision they rely on.

| tool | covers |
|---|---|
| Case plan | 13 situations → forum, deadlines, cost, paperwork, next steps |
| Deadlines | 20 limitation rules, with Section 4 resolved against a court calendar |
| Forum router | 13 problem types, tiered by claim value where it matters |
| Documents | 9 templates — RTI, consumer notice, Section 138 demand, and others |
| Court fees | 7 matter types, State slabs where they apply |
| Case timeline | 7 matter types, every stage dated at once |
| Stamp duty | 8 instruments |
| Maintenance | statutory range with the precedents behind it |
| Citations | pulls the authorities out of a judgment |

The **case plan** is the entry point: one situation and one date produce the
whole answer, composed from the tools above rather than reimplementing them, so
it can never disagree with the calculator it came from.

The lookup tables are also served to the browser and the arithmetic repeated
there, so the deadline calculator **works with no network**. The duplication is
held honest by a parity check that runs every rule through both implementations.

---

## Project structure

```
Nyaysetu/
├── frontend/                     # Next.js 16 App Router, Tailwind v4
│   └── src/
│       ├── app/                  # routes: analyze, toolkit, lawyers, cases…
│       ├── components/           # Chatbot, PassageReader, toolkit/*
│       └── lib/
│           ├── i18n/             # 100 keys × 8 locales
│           ├── toolkit/          # client-side lookup tables (offline)
│           └── auth/             # session + sign-in gate
│
├── backend/
│   ├── app/
│   │   ├── rag/
│   │   │   ├── corpus*.py        # 152 passages, three volumes
│   │   │   ├── retriever.py      # BM25 + embeddings, fused by rank
│   │   │   ├── lexicon.py        # cross-lingual bridge
│   │   │   ├── engine.py         # provider chain + prompt
│   │   │   ├── eval.py           # the gate
│   │   │   └── feedback.py       # where the corpus is thin (opt-in)
│   │   ├── tools/                # limitation, forum, fees, plan, …
│   │   └── routers/              # auth, bot, cases, tools, analyze
│   └── scripts/
│       ├── ablate.py             # which part of the stack does the work
│       ├── check_offline_parity.py
│       ├── check_fabrication.py
│       └── gaps.py
│
├── Dockerfile                    # Hugging Face Space
└── render.yaml                   # Render web service
```

---

## Getting started

**Prerequisites:** Node.js ≥ 20, Python ≥ 3.10.

```bash
# Backend
cd backend
python -m venv venv
venv\Scripts\activate          # Windows;  source venv/bin/activate elsewhere
pip install -r requirements.txt
cp .env.example .env           # everything in it is optional
uvicorn app.main:app --reload --port 8000
```

```bash
# Frontend
cd frontend
npm install
npm run dev                    # http://localhost:3000
```

API docs at **http://localhost:8000/docs**.

The assistant works with no configuration at all — it answers from the corpus
extractively. Everything in `.env` only improves how an answer is *phrased*,
never its legal content.

### Optional: better phrasing

```bash
ollama pull gemma3:4b          # local, no key, no quota
```

Note that `NYAYSETU_DISABLE_OLLAMA=1` is set in both production configs. A 4B
model asked in Hindi who the current Chief Justice is answers with a name from
its training data that the corpus never contains, and naming a sitting judge
wrongly is worse than the few seconds it saves. See `check_fabrication.py`.

---

## Checks

Run from `backend/`. On Windows set `PYTHONIOENCODING=utf-8`, or the Indic
output crashes on cp1252.

| command | what it answers |
|---|---|
| `python -m app.rag.eval` | Does retrieval still work, in every language? |
| `python -m scripts.ablate` | Which part of the stack is doing the work? |
| `python scripts/check_offline_parity.py` | Do server and browser agree? (160 cases) |
| `python -m scripts.check_fabrication` | Does the model invent facts? (8 languages) |
| `python -m scripts.gaps` | Where is the corpus thin? (needs the opt-in log) |

Frontend: `npx tsc --noEmit` and `npm run build`.

---

## API

| group | endpoints |
|---|---|
| Assistant | `POST /api/bot/chat`, `/chat/stream`, `GET /api/bot/health` |
| Toolkit | `GET,POST /api/tools/{plan,limitation,forum,documents,fees,timeline,stamp-duty,maintenance}` |
| | `POST /api/tools/citations`, `GET /api/tools/{calendar,bundle}` |
| Analyze | `POST /api/analyze`, `GET /api/analyze/refine/{id}` |
| Auth | `POST /api/auth/{register,login}` |
| Cases | `GET,POST /api/cases`, `PATCH /api/cases/{id}/{assign,status}` |
| Deadlines | `GET,POST /api/deadlines`, `GET /api/deadlines/digest` |
| Directory | `GET /api/lawyers` |
| Messaging | `POST /api/chat`, `GET /api/chat/{user_id}` |

Full schema at `/docs`.

---

## Privacy

The feedback log that records where retrieval misses is **off unless
`NYAYSETU_FEEDBACK_LOG` is set**. It stores no user id, account or IP; the
session key groups two consecutive requests and maps to nothing. Question text
is kept only under a second flag, and the log is gitignored — these are people's
legal problems.

---

## Deployment

Live:

| | |
|---|---|
| Frontend | https://nyay-setu-sigma.vercel.app |
| Backend | https://amandadsena07-nyaysetu-backend.hf.space |
| API docs | https://amandadsena07-nyaysetu-backend.hf.space/docs |

Vercel builds the frontend from `main` on push. The Space is a **backend-only**
tree — `Dockerfile`, `README.md` and `backend/`, nothing else. Pushing the whole
repo there fails: the Space rejects the frontend's PNGs for not being in LFS,
and a backend image has no use for them. To redeploy it:

```bash
git archive main Dockerfile README.md .dockerignore .gitattributes backend \
  | tar -x -C /tmp/hfdeploy
cd /tmp/hfdeploy && git init -b main && git add -A && git commit -m "Deploy"
git remote add space https://huggingface.co/spaces/<user>/<space>
git push space main --force
```

`render.yaml` is kept as an alternative host. It generates `JWT_SECRET_KEY`
itself; only `DATABASE_URL` and the optional `GEMINI_API_KEY` need setting.

**Set `DATABASE_URL` to a Postgres URL** (Neon and Supabase have free tiers that
persist) on whichever host you use. Without it the app falls back to SQLite on
an ephemeral disk and every account disappears on restart. Everything that does
not need an account — the assistant, the whole toolkit — works regardless.

---

## Disclaimer

Nyaysetu provides **legal information, not legal advice**. Every answer cites
the provision it rests on so it can be checked. For a decision that matters,
consult an advocate — free legal aid is a statutory right for most of the people
this is built for, and the assistant will tell you how to claim it.

## License

MIT
