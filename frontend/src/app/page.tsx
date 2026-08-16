"use client";

/**
 * Landing page.
 *
 * Rewritten to remove invented figures. The previous version advertised "142
 * Lawyers", a "94% Match Rate", "SOC2 Compliant Storage" and "End-to-end
 * Encrypted" messaging; none of those were true, and the encryption claim in
 * particular invited people to type legal problems into a box on a promise the
 * software did not keep.
 *
 * What replaced them is the real thing, which turned out to be the better
 * pitch: a live reading of the running backend, the project's own evaluation
 * scores, the actual size of the corpus and toolkit, and a plainly-stated
 * section on what this tool gets wrong. Every number on this page traces to
 * `lib/site-stats.ts`, which records the command that produces it.
 */

import Link from "next/link";
import {
  AlertTriangle,
  ArrowRight,
  BadgeIndianRupee,
  BookOpen,
  CalendarClock,
  CheckCircle2,
  FileSearch,
  FileText,
  Filter,
  Landmark,
  MapPin,
  Scale,
  ScrollText,
  Search,
  Sparkles,
  Timer,
} from "lucide-react";

import { LiveStatus } from "@/components/LiveStatus";
import { AnswerPreview } from "@/components/AnswerPreview";
import { Reveal } from "@/components/motion/Reveal";
import { CountUp } from "@/components/motion/CountUp";
import { LOCALE_LIST } from "@/lib/i18n/locales";
import {
  CORPUS_STATS,
  CROSS_LINGUAL_STATS,
  EVAL_STATS,
  KNOWN_GAPS,
  TOOLKIT_STATS,
  type SiteStat,
} from "@/lib/site-stats";

/* These are annotated `SiteStat[]` rather than left to inference. The entries
   are heterogeneous — only some carry `decimals` or `suffix` — and the inferred
   union would make those properties unreachable without an `in` check that
   narrows to `unknown`. Declaring the common shape is the simpler fix. */
const RETRIEVAL_FIGURES: SiteStat[] = [
  EVAL_STATS.hitAt1,
  EVAL_STATS.hitAt3,
  EVAL_STATS.mrr,
  EVAL_STATS.falsePositives,
];

const CROSS_LINGUAL_FIGURES: SiteStat[] = [
  CROSS_LINGUAL_STATS.questions,
  CROSS_LINGUAL_STATS.answered,
  CROSS_LINGUAL_STATS.hitAt1,
];

const CORPUS_FIGURES: SiteStat[] = [
  CORPUS_STATS.passages,
  CORPUS_STATS.acts,
  CORPUS_STATS.lexicon,
  CORPUS_STATS.languages,
];

// ── The toolkit, with the real size of each lookup table ──────────────────
const TOOLS = [
  {
    icon: Sparkles,
    name: "Case plan",
    blurb: "One situation and one date produce the forum, the deadline, the cost and the paperwork — composed from the tools below, so it can never disagree with them.",
    count: `${TOOLKIT_STATS.situations.value} situations`,
    accent: "text-amber-600 bg-amber-50",
  },
  {
    icon: CalendarClock,
    name: "Deadlines",
    blurb: "Limitation periods worked out against a real court calendar, with Section 4 resolved when the last day falls on a holiday.",
    count: `${TOOLKIT_STATS.limitationRules.value} rules`,
    accent: "text-rose-600 bg-rose-50",
  },
  {
    icon: MapPin,
    name: "Forum router",
    blurb: "Which court, tribunal or commission hears your kind of problem — tiered by claim value where that decides it.",
    count: `${TOOLKIT_STATS.forumRules.value} problem types`,
    accent: "text-blue-600 bg-blue-50",
  },
  {
    icon: FileText,
    name: "Documents",
    blurb: "RTI applications, consumer notices, a Section 138 demand, a vakalatnama — drafted with the fee, the stamps and the filing steps spelled out.",
    count: `${TOOLKIT_STATS.templates.value} templates`,
    accent: "text-violet-600 bg-violet-50",
  },
  {
    icon: BadgeIndianRupee,
    name: "Court fees",
    blurb: "What filing actually costs, with State slabs applied where they differ.",
    count: `${TOOLKIT_STATS.feeMatters.value} matter types`,
    accent: "text-emerald-600 bg-emerald-50",
  },
  {
    icon: Timer,
    name: "Case timeline",
    blurb: "Every stage of a matter dated at once, so you can see the whole road rather than the next step.",
    count: `${TOOLKIT_STATS.timelineMatters.value} matter types`,
    accent: "text-sky-600 bg-sky-50",
  },
  {
    icon: ScrollText,
    name: "Stamp duty",
    blurb: "What to pay on a sale deed, a lease, a gift or a power of attorney before it is enforceable.",
    count: `${TOOLKIT_STATS.stampInstruments.value} instruments`,
    accent: "text-orange-600 bg-orange-50",
  },
  {
    icon: Scale,
    name: "Maintenance",
    blurb: "The statutory range, with the precedents that set it.",
    count: "With citations",
    accent: "text-teal-600 bg-teal-50",
  },
  {
    icon: FileSearch,
    name: "Citations",
    blurb: "Paste a judgment and get the authorities it relies on, pulled out and listed.",
    count: "From any judgment",
    accent: "text-indigo-600 bg-indigo-50",
  },
] as const;

const STEPS = [
  {
    icon: Search,
    title: "Retrieval finds the law",
    body: `A keyword index built for legal vocabulary, a ${CORPUS_STATS.lexicon.value.toLocaleString("en-IN")}-entry lexicon that maps legal terms across seven Indian languages onto the English the corpus uses, and optional multilingual embeddings — fused together by rank.`,
  },
  {
    icon: Filter,
    title: "Guards decide whether to answer at all",
    body: "Several checks have to agree before anything is produced. Deciding a question is out of corpus is treated as a feature, because a confident wrong answer is the worst outcome a legal tool can have.",
  },
  {
    icon: BookOpen,
    title: "Generation only phrases it",
    body: "The model never supplies the law, only the wording. If no model is configured, the answer is composed straight from the retrieved passages — which cannot invent a section number, because it never writes one.",
  },
] as const;

const FAQS = [
  {
    q: "Do I need an account?",
    a: "No. The assistant, the entire toolkit and the knowledge base all work signed out. An account is only needed for the case board and messaging, which are person-to-person by nature.",
  },
  {
    q: "Is this free?",
    a: "Yes, and it is open source under the MIT licence. There is no paid tier and nothing here is for sale.",
  },
  {
    q: "How do I know an answer is right?",
    a: "Every answer names the Act and the section it rests on, and shows you the passage it was built from. If an answer does not cite a provision, treat it as unverified — that is the whole design.",
  },
  {
    q: "Which languages does it handle?",
    a: `Eight: English, Hindi, Marathi, Gujarati, Tamil, Telugu, Bengali and Kannada. Cross-lingual retrieval is scored separately from English in the evaluation, because an aggregate dominated by English would hide a failure in the others completely.`,
  },
  {
    q: "Can it replace an advocate?",
    a: "No. It gives legal information, not legal advice, and it has no view on your particular facts. Free legal aid is a statutory right for most people in India — call 15100.",
  },
  {
    q: "Does the deadline calculator work offline?",
    a: "Yes. The lookup tables are sent to your browser and the arithmetic repeated there, so it keeps working without a network. A parity check runs every rule through both implementations to keep them in agreement.",
  },
] as const;

export default function Home() {
  return (
    <div className="bg-white font-sans text-slate-900">
      {/* ═══ HERO ═══ */}
      <section className="relative overflow-hidden px-6 pt-20 pb-24">
        {/* Ambient mesh. Decorative, and explicitly out of the a11y tree. */}
        <div aria-hidden="true" className="pointer-events-none absolute inset-0 -z-10">
          <div className="animate-aurora absolute -top-40 -left-32 h-[34rem] w-[34rem] rounded-full bg-amber-200/35 blur-3xl" />
          <div className="animate-aurora absolute -top-24 right-0 h-[30rem] w-[30rem] rounded-full bg-violet-200/30 blur-3xl [animation-delay:-7s]" />
          <div className="animate-aurora absolute top-64 left-1/3 h-[26rem] w-[26rem] rounded-full bg-sky-200/25 blur-3xl [animation-delay:-14s]" />
        </div>

        <div className="mx-auto max-w-6xl text-center">
          <div className="animate-fade-in-up inline-flex items-center gap-2 rounded-full border border-amber-200/70 bg-amber-50/70 px-4 py-1.5 text-sm font-medium text-amber-900 backdrop-blur-sm">
            <Landmark className="h-4 w-4" aria-hidden="true" />
            Open-source legal information for India
          </div>

          <h1
            className="animate-fade-in-up mt-7 font-serif text-5xl leading-[1.08] font-bold tracking-tight text-balance md:text-6xl lg:text-7xl"
            style={{ animationDelay: "0.08s" }}
          >
            The law, in the language
            <br className="hidden sm:block" /> you think in —{" "}
            <span className="animate-gradient-pan bg-gradient-to-r from-amber-600 via-orange-500 to-amber-700 bg-clip-text text-transparent">
              cited to the section.
            </span>
          </h1>

          <p
            className="animate-fade-in-up mx-auto mt-7 max-w-2xl text-lg leading-relaxed text-gray-600 md:text-xl"
            style={{ animationDelay: "0.16s" }}
          >
            Nyaysetu answers from curated Indian statute and shows you the
            provision it used, so you can check it. Plus a toolkit for the
            deadline, the forum, the paperwork and what it all costs — no
            account, no cost.
          </p>

          <div
            className="animate-fade-in-up mt-9 flex flex-wrap items-center justify-center gap-3"
            style={{ animationDelay: "0.24s" }}
          >
            <Link
              href="/toolkit"
              transitionTypes={["nav-forward"]}
              className="lift inline-flex items-center gap-2 rounded-full bg-slate-900 px-7 py-3.5 text-base font-medium text-white shadow-lg shadow-slate-900/15 hover:bg-slate-800"
            >
              Open the toolkit
              <ArrowRight className="h-4 w-4" aria-hidden="true" />
            </Link>
            <Link
              href="/how-it-works"
              transitionTypes={["nav-forward"]}
              className="lift inline-flex items-center gap-2 rounded-full border border-gray-200 bg-white/80 px-7 py-3.5 text-base font-medium text-slate-900 backdrop-blur-sm hover:border-gray-300"
            >
              How it works
            </Link>
          </div>

          <div
            className="animate-fade-in-up mt-9"
            style={{ animationDelay: "0.32s" }}
          >
            <LiveStatus />
          </div>

          <div
            className="animate-fade-in-up mt-16"
            style={{ animationDelay: "0.4s" }}
          >
            <AnswerPreview />
          </div>
        </div>
      </section>

      {/* ═══ HOW IT WORKS ═══ */}
      <section className="border-y border-gray-100 bg-gray-50/60 px-6 py-24">
        <div className="mx-auto max-w-6xl">
          <Reveal as="header" className="mx-auto mb-16 max-w-2xl text-center">
            <p className="mb-3 text-sm font-semibold tracking-[0.12em] text-amber-700 uppercase">
              Retrieval first
            </p>
            <h2 className="mb-5 font-serif text-4xl font-bold tracking-tight md:text-5xl">
              The model does not decide what the law says
            </h2>
            <p className="text-lg leading-relaxed text-gray-600">
              Most systems ask a language model a legal question and hope. This
              one inverts that dependency: retrieval produces the law, and
              generation is only allowed to phrase it.
            </p>
          </Reveal>

          <ol className="grid gap-6 md:grid-cols-3">
            {STEPS.map((step, i) => (
              <Reveal as="li" key={step.title} delay={i * 0.1}>
                <div className="lift group h-full rounded-3xl border border-gray-200 bg-white p-8 hover:border-amber-300 hover:shadow-xl hover:shadow-amber-900/5">
                  <div className="mb-6 flex items-center gap-3">
                    <span className="flex h-11 w-11 items-center justify-center rounded-2xl bg-slate-900 text-white">
                      <step.icon className="h-5 w-5" aria-hidden="true" />
                    </span>
                    <span className="font-mono text-4xl font-bold text-gray-200 transition-colors group-hover:text-amber-200">
                      {String(i + 1).padStart(2, "0")}
                    </span>
                  </div>
                  <h3 className="mb-3 font-serif text-xl font-semibold">
                    {step.title}
                  </h3>
                  <p className="text-[15px] leading-relaxed text-gray-600">
                    {step.body}
                  </p>
                </div>
              </Reveal>
            ))}
          </ol>
        </div>
      </section>

      {/* ═══ MEASURED ═══ */}
      <section className="px-6 py-24">
        <div className="mx-auto max-w-6xl">
          <Reveal as="header" className="mx-auto mb-16 max-w-2xl text-center">
            <p className="mb-3 text-sm font-semibold tracking-[0.12em] text-amber-700 uppercase">
              Measured, not asserted
            </p>
            <h2 className="mb-5 font-serif text-4xl font-bold tracking-tight md:text-5xl">
              Every claim here has a command behind it
            </h2>
            <p className="text-lg leading-relaxed text-gray-600">
              A single evaluation gates every change to the corpus, the lexicon
              or the retriever, and it exits non-zero on regression. These are
              its current numbers.
            </p>
          </Reveal>

          <div className="mb-8 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
            {CORPUS_FIGURES.map((stat, i) => (
              <Reveal key={stat.label} delay={i * 0.07}>
                <div className="lift h-full rounded-3xl border border-gray-200 bg-gradient-to-br from-white to-gray-50/80 p-7 hover:border-slate-300 hover:shadow-lg">
                  <div className="mb-2 font-serif text-4xl font-bold tracking-tight text-slate-900">
                    <CountUp value={stat.value} />
                  </div>
                  <div className="text-sm font-medium text-gray-500">
                    {stat.label}
                  </div>
                </div>
              </Reveal>
            ))}
          </div>

          <Reveal delay={0.1}>
            <div className="grid gap-5 lg:grid-cols-2">
              {/* Retrieval quality */}
              <div className="rounded-3xl border border-gray-200 bg-slate-950 p-8 text-slate-200 md:p-10">
                <h3 className="mb-2 font-serif text-2xl font-semibold text-white">
                  Retrieval quality
                </h3>
                <p className="mb-8 text-sm text-slate-400">
                  Over {EVAL_STATS.questions.value} questions, against{" "}
                  {CORPUS_STATS.passages.value} passages.
                </p>
                <dl className="grid grid-cols-2 gap-x-6 gap-y-7">
                  {RETRIEVAL_FIGURES.map((stat) => (
                    <div key={stat.label}>
                      <dd className="mb-1.5 font-mono text-3xl font-bold text-amber-400">
                        <CountUp
                          value={stat.value}
                          decimals={stat.decimals}
                          suffix={stat.suffix}
                        />
                        {stat.label.startsWith("Guard-set") && (
                          <span className="text-lg text-amber-400/60">/14</span>
                        )}
                      </dd>
                      <dt className="text-xs leading-relaxed text-slate-400">
                        {stat.label}
                      </dt>
                    </div>
                  ))}
                </dl>
              </div>

              {/* Cross-lingual */}
              <div className="rounded-3xl border border-amber-200 bg-gradient-to-br from-amber-50 to-orange-50/50 p-8 md:p-10">
                <h3 className="mb-2 font-serif text-2xl font-semibold text-amber-950">
                  Scored separately in every language
                </h3>
                <p className="mb-8 text-sm leading-relaxed text-amber-900/70">
                  An aggregate dominated by English hides an Indic-language
                  failure completely, so the cross-lingual block is reported on
                  its own. It has caught regressions that every English metric
                  stayed green through.
                </p>
                <dl className="grid grid-cols-3 gap-4">
                  {CROSS_LINGUAL_FIGURES.map((stat) => (
                    <div key={stat.label}>
                      <dd className="mb-1.5 font-mono text-3xl font-bold text-amber-700">
                        <CountUp value={stat.value} suffix={stat.suffix} />
                      </dd>
                      <dt className="text-xs leading-relaxed text-amber-900/70">
                        {stat.label}
                      </dt>
                    </div>
                  ))}
                </dl>
              </div>
            </div>
          </Reveal>
        </div>
      </section>

      {/* ═══ TOOLKIT ═══ */}
      <section className="border-y border-gray-100 bg-gray-50/60 px-6 py-24">
        <div className="mx-auto max-w-6xl">
          <Reveal as="header" className="mx-auto mb-16 max-w-2xl text-center">
            <p className="mb-3 text-sm font-semibold tracking-[0.12em] text-amber-700 uppercase">
              The toolkit
            </p>
            <h2 className="mb-5 font-serif text-4xl font-bold tracking-tight md:text-5xl">
              The things people otherwise pay someone to work out
            </h2>
            <p className="text-lg leading-relaxed text-gray-600">
              None of this calls a model. Lookup tables and calendar arithmetic,
              so answers are instant, identical every time, and cite the
              provision they rely on.
            </p>
          </Reveal>

          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {TOOLS.map((tool, i) => (
              <Reveal key={tool.name} delay={(i % 3) * 0.08}>
                <Link
                  href="/toolkit"
                  transitionTypes={["nav-forward"]}
                  className="lift group relative block h-full overflow-hidden rounded-3xl border border-gray-200 bg-white p-7 hover:border-slate-300 hover:shadow-xl hover:shadow-slate-900/5"
                >
                  {/* Light sweep on hover */}
                  <span
                    aria-hidden="true"
                    className="animate-sheen pointer-events-none absolute inset-y-0 -left-full w-1/2 bg-gradient-to-r from-transparent via-white/60 to-transparent"
                  />
                  <span
                    className={`mb-5 flex h-12 w-12 items-center justify-center rounded-2xl ${tool.accent}`}
                  >
                    <tool.icon className="h-5 w-5" aria-hidden="true" />
                  </span>
                  <h3 className="mb-2 font-serif text-xl font-semibold">
                    {tool.name}
                  </h3>
                  <p className="mb-5 text-[15px] leading-relaxed text-gray-600">
                    {tool.blurb}
                  </p>
                  <span className="inline-flex items-center gap-1.5 rounded-full bg-gray-50 px-3 py-1 text-xs font-medium text-gray-600 transition-colors group-hover:bg-slate-900 group-hover:text-white">
                    {tool.count}
                  </span>
                </Link>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ LANGUAGES ═══ */}
      <section className="overflow-hidden px-6 py-24">
        <Reveal as="header" className="mx-auto mb-14 max-w-2xl text-center">
          <p className="mb-3 text-sm font-semibold tracking-[0.12em] text-amber-700 uppercase">
            Eight languages
          </p>
          <h2 className="mb-5 font-serif text-4xl font-bold tracking-tight md:text-5xl">
            Ask in the language you would ask a person in
          </h2>
          <p className="text-lg leading-relaxed text-gray-600">
            A lexicon of{" "}
            {CORPUS_STATS.lexicon.value.toLocaleString("en-IN")} entries bridges
            legal terms in seven Indian languages onto the English the corpus
            uses, with prefix and stem matching so inflected forms still land.
          </p>
        </Reveal>

        {/* Marquee. Duplicated once so the loop is seamless; the copy is hidden
            from screen readers so the languages are not announced twice. */}
        <div className="marquee-track relative">
          <div
            aria-hidden="true"
            className="pointer-events-none absolute inset-y-0 left-0 z-10 w-24 bg-gradient-to-r from-white to-transparent"
          />
          <div
            aria-hidden="true"
            className="pointer-events-none absolute inset-y-0 right-0 z-10 w-24 bg-gradient-to-l from-white to-transparent"
          />
          <div className="flex w-max">
            {[0, 1].map((copy) => (
              <ul
                key={copy}
                aria-hidden={copy === 1}
                className="animate-marquee flex shrink-0 gap-4 pr-4"
              >
                {LOCALE_LIST.map((locale) => (
                  <li
                    key={locale.code}
                    lang={locale.code}
                    className="lift flex min-w-[13rem] items-center gap-4 rounded-2xl border border-gray-200 bg-white px-6 py-5 hover:border-amber-300"
                  >
                    <span className="font-serif text-2xl font-semibold text-slate-900">
                      {locale.native}
                    </span>
                    <span className="text-sm text-gray-400">{locale.label}</span>
                  </li>
                ))}
              </ul>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ WHAT IT WILL NOT DO ═══ */}
      <section className="border-y border-gray-100 bg-slate-950 px-6 py-24 text-slate-300">
        <div className="mx-auto max-w-5xl">
          <Reveal as="header" className="mx-auto mb-14 max-w-2xl text-center">
            <p className="mb-3 inline-flex items-center gap-2 text-sm font-semibold tracking-[0.12em] text-amber-500 uppercase">
              <AlertTriangle className="h-4 w-4" aria-hidden="true" />
              Known limits
            </p>
            <h2 className="mb-5 font-serif text-4xl font-bold tracking-tight text-white md:text-5xl">
              Where this tool falls short
            </h2>
            <p className="text-lg leading-relaxed text-slate-400">
              Published rather than buried. A tool that tells you what it cannot
              do is worth more than one that implies it can do everything —
              particularly this one, where the cost of a confident wrong answer
              is somebody&rsquo;s case.
            </p>
          </Reveal>

          <div className="grid gap-5 md:grid-cols-3">
            {KNOWN_GAPS.map((item, i) => (
              <Reveal key={item.gap} delay={i * 0.08}>
                <div className="h-full rounded-3xl border border-white/10 bg-white/[0.03] p-7">
                  <h3 className="mb-3 font-serif text-lg font-semibold text-white">
                    {item.gap}
                  </h3>
                  <p className="text-sm leading-relaxed text-slate-400">
                    {item.detail}
                  </p>
                </div>
              </Reveal>
            ))}
          </div>

          <Reveal delay={0.2}>
            <p className="mt-10 text-center text-sm text-slate-500">
              For a decision that matters, consult an advocate. Free legal aid is
              a statutory right for most people in India —{" "}
              <a
                href="tel:15100"
                className="font-medium text-amber-400 underline underline-offset-4 hover:text-amber-300"
              >
                call 15100
              </a>
              .
            </p>
          </Reveal>
        </div>
      </section>

      {/* ═══ FAQ ═══ */}
      <section className="px-6 py-24">
        <div className="mx-auto max-w-3xl">
          <Reveal as="header" className="mb-14 text-center">
            <h2 className="mb-5 font-serif text-4xl font-bold tracking-tight md:text-5xl">
              Questions people ask first
            </h2>
          </Reveal>

          <div className="space-y-3">
            {FAQS.map((faq, i) => (
              <Reveal key={faq.q} delay={(i % 3) * 0.06}>
                {/* Native <details> — keyboard accessible, works without JS,
                    and searchable by the browser's own find-in-page. */}
                <details className="group rounded-2xl border border-gray-200 bg-white transition-colors open:border-amber-300 open:bg-amber-50/30 hover:border-gray-300">
                  <summary className="flex cursor-pointer items-center justify-between gap-4 px-6 py-5 font-medium text-slate-900 [&::-webkit-details-marker]:hidden">
                    {faq.q}
                    <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full border border-gray-200 text-gray-400 transition-transform duration-300 group-open:rotate-45 group-open:border-amber-400 group-open:text-amber-600">
                      <span className="text-lg leading-none">+</span>
                    </span>
                  </summary>
                  <p className="px-6 pb-6 text-[15px] leading-relaxed text-gray-600">
                    {faq.a}
                  </p>
                </details>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ CTA ═══ */}
      <section className="px-6 pb-24">
        <Reveal>
          <div className="relative mx-auto max-w-5xl overflow-hidden rounded-[2.5rem] border border-amber-200 bg-gradient-to-br from-amber-50 via-orange-50/60 to-white p-12 text-center md:p-16">
            <div
              aria-hidden="true"
              className="animate-aurora pointer-events-none absolute -top-24 left-1/2 h-72 w-[36rem] -translate-x-1/2 rounded-full bg-amber-300/25 blur-3xl"
            />
            <div className="relative">
              <h2 className="mb-5 font-serif text-4xl font-bold tracking-tight text-balance md:text-5xl">
                Start with the question you actually have
              </h2>
              <p className="mx-auto mb-9 max-w-xl text-lg leading-relaxed text-gray-600">
                No account, no cost, and an answer that shows you the provision
                it came from.
              </p>
              <div className="flex flex-wrap items-center justify-center gap-3">
                <Link
                  href="/toolkit"
                  transitionTypes={["nav-forward"]}
                  className="lift inline-flex items-center gap-2 rounded-full bg-slate-900 px-8 py-4 text-base font-medium text-white shadow-lg shadow-slate-900/15 hover:bg-slate-800"
                >
                  Open the toolkit
                  <ArrowRight className="h-4 w-4" aria-hidden="true" />
                </Link>
                <Link
                  href="/knowledge"
                  transitionTypes={["nav-forward"]}
                  className="lift inline-flex items-center gap-2 rounded-full border border-gray-300 bg-white px-8 py-4 text-base font-medium text-slate-900 hover:border-slate-400"
                >
                  Browse the knowledge base
                </Link>
              </div>
              <p className="mt-8 inline-flex items-center gap-2 text-sm text-gray-500">
                <CheckCircle2 className="h-4 w-4 text-emerald-600" aria-hidden="true" />
                Works signed out · Open source · Answers cite their source
              </p>
            </div>
          </div>
        </Reveal>
      </section>
    </div>
  );
}
