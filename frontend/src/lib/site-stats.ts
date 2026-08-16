/**
 * Every number this site puts on screen.
 *
 * The rule for this file is simple: **a figure may live here only if someone
 * can re-derive it from the repository.** Each entry carries the command that
 * produces it. Nothing aspirational, nothing rounded up, nothing borrowed from
 * a market-size slide.
 *
 * This exists because the landing page previously advertised "142 Lawyers",
 * "94% Match Rate" and "SOC2 Compliant Storage", none of which were true. A
 * legal-information tool that misrepresents itself on the way in has no
 * business asking anyone to trust what it says about their limitation period.
 *
 * All values below were re-derived against the backend on 2026-08-16.
 *
 * Note on `acts`: the corpus stores an act label per passage, and 45 of those
 * labels name two statutes at once ("Information Technology Act, 2000 and
 * Bharatiya Nyaya Sanhita, 2023"). 107 counts distinct labels, so the true
 * number of distinct statutes is somewhat higher. Understating is the safe
 * direction to be wrong in.
 */

export interface SiteStat {
  value: number;
  label: string;
  decimals?: number;
  prefix?: string;
  suffix?: string;
  /** How to reproduce this number. Shown to no one; kept honest for the next reader. */
  source: string;
}

/** What the assistant answers from. */
export const CORPUS_STATS = {
  passages: {
    value: 152,
    label: "Provisions indexed",
    source: "python -c 'from app.rag.corpus import CORPUS; print(len(CORPUS))'",
  },
  acts: {
    value: 107,
    label: "Acts & codes cited",
    source: "distinct `Passage.act` labels in app/rag/corpus.py",
  },
  lexicon: {
    value: 2009,
    label: "Cross-lingual terms",
    source: "python -c 'from app.rag.lexicon import LEXICON; print(len(LEXICON))'",
  },
  languages: {
    value: 8,
    label: "Languages",
    source: "LOCALE_CODES in src/lib/i18n/locales.ts",
  },
} satisfies Record<string, SiteStat>;

/**
 * Retrieval quality, from `python -m app.rag.eval` — the gate that has to pass
 * before any corpus, lexicon or retriever change lands.
 */
export const EVAL_STATS = {
  questions: {
    value: 131,
    label: "Questions in the eval set",
    source: "python -m app.rag.eval",
  },
  hitAt1: {
    value: 92.4,
    decimals: 1,
    suffix: "%",
    label: "Correct provision ranked first",
    source: "python -m app.rag.eval — hit@1",
  },
  hitAt3: {
    value: 100,
    suffix: "%",
    label: "Correct provision in top three",
    source: "python -m app.rag.eval — hit@3",
  },
  mrr: {
    value: 0.961,
    decimals: 3,
    label: "Mean reciprocal rank",
    source: "python -m app.rag.eval — MRR",
  },
  falsePositives: {
    value: 14,
    label: "Guard-set questions correctly refused",
    // Precision matters here. The eval reports "false positives 0/14" for its
    // guard set — 14 out of 14 refused, which is what this figure means. It is
    // NOT a claim that the assistant never answers something it should not:
    // the same run reports "Out of scope — should refuse: 3/3 answered", a
    // real and currently-open gap. See KNOWN_GAPS below.
    source: "python -m app.rag.eval — false positives 0/14",
  },
} satisfies Record<string, SiteStat>;

/**
 * What the eval says is still wrong.
 *
 * Published rather than buried. A tool that tells people what it cannot do is
 * more trustworthy than one that implies it can do everything, and anyone
 * relying on this for a real legal problem deserves to know where the edges
 * are. Re-check with `python -m app.rag.eval` after any retrieval change.
 */
export const KNOWN_GAPS = [
  {
    gap: "Questions about government recruitment and exam dates",
    detail:
      "Three out-of-scope questions in the eval — variations of \"when is the police recruitment exam\" in English, Marathi and Kannada — are answered from legal provisions instead of being refused. The corpus has nothing on recruitment, so the retriever reaches for the nearest legal topic it does have.",
  },
  {
    gap: "Anything that turns on facts specific to your case",
    detail:
      "The toolkit computes from the dates and categories you enter. It cannot read your documents, weigh evidence, or tell you whether a court will accept a condonation of delay.",
  },
  {
    gap: "Current case status, cause lists and judge assignments",
    detail:
      "The corpus is statute, not live court data. Nothing here knows what happened in your matter this morning.",
  },
] as const;

/**
 * Cross-lingual retrieval is scored separately on purpose: an aggregate
 * dominated by English hides an Indic-language failure completely.
 */
export const CROSS_LINGUAL_STATS = {
  questions: {
    value: 70,
    label: "Questions across seven Indian languages",
    source: "python -m app.rag.eval — cross-lingual block",
  },
  answered: {
    value: 100,
    suffix: "%",
    label: "Answered",
    source: "python -m app.rag.eval — cross-lingual block",
  },
  hitAt1: {
    value: 93,
    suffix: "%",
    label: "Correct provision ranked first",
    source: "python -m app.rag.eval — cross-lingual hit@1",
  },
} satisfies Record<string, SiteStat>;

/**
 * Toolkit coverage. None of these call a model — they are lookup tables and
 * calendar arithmetic, which is why they answer instantly and identically
 * every time. Counts come from the length of each table.
 */
export const TOOLKIT_STATS = {
  situations: { value: 13, label: "Situations the case plan covers", source: "len(app.tools.plan.SITUATIONS)" },
  limitationRules: { value: 20, label: "Limitation rules", source: "len(app.tools.limitation.RULES)" },
  forumRules: { value: 13, label: "Problem types routed to a forum", source: "len(app.tools.forum.RULES)" },
  templates: { value: 9, label: "Document templates", source: "len(app.tools.documents.TEMPLATES)" },
  feeMatters: { value: 7, label: "Matter types with court fees", source: "len(app.tools.fees.MATTERS)" },
  timelineMatters: { value: 7, label: "Matter types with a dated timeline", source: "len(app.tools.timeline.MATTERS)" },
  stampInstruments: { value: 8, label: "Instruments with stamp duty", source: "len(app.tools.stamp_duty.INSTRUMENTS)" },
} satisfies Record<string, SiteStat>;

/**
 * The National Legal Services Authority helpline. Free legal aid is a
 * statutory right under the Legal Services Authorities Act, 1987 for most of
 * the people this app is built for, and this number is the way to claim it.
 * It belongs on every page.
 */
export const LEGAL_AID_HELPLINE = "15100";
