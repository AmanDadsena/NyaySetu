import type { Metadata } from "next";
import Link from "next/link";
import {
  ArrowRight,
  BookOpen,
  Filter,
  Languages,
  Quote,
  Ruler,
  Search,
  ShieldCheck,
  WifiOff,
} from "lucide-react";
import { Reveal } from "@/components/motion/Reveal";
import { CountUp } from "@/components/motion/CountUp";
import {
  CORPUS_STATS,
  CROSS_LINGUAL_STATS,
  EVAL_STATS,
  type SiteStat,
} from "@/lib/site-stats";

/* Annotated so the optional `suffix` stays reachable — see the same note in
   the landing page. */
const CROSS_LINGUAL_FIGURES: SiteStat[] = [
  CROSS_LINGUAL_STATS.questions,
  CROSS_LINGUAL_STATS.answered,
  CROSS_LINGUAL_STATS.hitAt1,
];

export const metadata: Metadata = {
  title: "How it works — Nyaysetu",
  description:
    "Retrieval produces the law and generation only phrases it. How Nyaysetu answers from cited statute rather than from a model's memory.",
};

const LAYERS = [
  {
    icon: Search,
    name: "BM25 over an inverted index",
    body: "A keyword index, strong precisely where legal language is exact. Someone who types \"Section 138\" or \"vakalatnama\" wants the passage containing that term, not the passage that is vaguely about it.",
  },
  {
    icon: Languages,
    name: "A cross-lingual lexicon",
    body: `${CORPUS_STATS.lexicon.value.toLocaleString("en-IN")} entries mapping legal terms in seven Indian languages onto the English the corpus uses, with prefix and stem matching so inflected forms still land. This is what lets a question typed in Kannada reach an English passage.`,
  },
  {
    icon: Ruler,
    name: "Multilingual embeddings, optional",
    body: "When the model is present, semantic matches are fused with the keyword results by reciprocal rank. When it is absent, the keyword path answers alone — which is why the assistant still works on a machine with no model and no network.",
  },
] as const;

export default function HowItWorksPage() {
  return (
    <div className="bg-white">
      {/* ═══ HERO ═══ */}
      <section className="relative overflow-hidden border-b border-gray-100 px-6 pt-20 pb-20">
        <div aria-hidden="true" className="pointer-events-none absolute inset-0 -z-10">
          <div className="animate-aurora absolute -top-40 left-1/4 h-[30rem] w-[30rem] rounded-full bg-sky-200/30 blur-3xl" />
          <div className="animate-aurora absolute -top-20 right-10 h-[26rem] w-[26rem] rounded-full bg-amber-200/30 blur-3xl [animation-delay:-9s]" />
        </div>

        <div className="mx-auto max-w-3xl text-center">
          <p className="animate-fade-in-up mb-5 text-sm font-semibold tracking-[0.12em] text-amber-700 uppercase">
            How it works
          </p>
          <h1
            className="animate-fade-in-up mb-6 font-serif text-5xl leading-tight font-bold tracking-tight text-balance md:text-6xl"
            style={{ animationDelay: "0.08s" }}
          >
            Retrieval produces the law.
            <br />
            Generation only phrases it.
          </h1>
          <p
            className="animate-fade-in-up text-lg leading-relaxed text-gray-600 md:text-xl"
            style={{ animationDelay: "0.16s" }}
          >
            Most legal chatbots ask a language model a question and print
            whatever comes back. That design cannot distinguish a real section
            number from a plausible one. This one inverts the dependency, and
            the whole architecture follows from that single decision.
          </p>
        </div>
      </section>

      {/* ═══ THE INVERSION ═══ */}
      <section className="px-6 py-24">
        <div className="mx-auto max-w-5xl">
          <Reveal>
            <div className="grid gap-5 md:grid-cols-2">
              <div className="rounded-3xl border border-rose-200 bg-rose-50/50 p-8">
                <p className="mb-4 inline-flex rounded-full bg-rose-100 px-3 py-1 text-xs font-semibold tracking-wide text-rose-700 uppercase">
                  The usual design
                </p>
                <h2 className="mb-4 font-serif text-2xl font-semibold text-slate-900">
                  The model is the source
                </h2>
                <p className="mb-5 text-[15px] leading-relaxed text-gray-700">
                  A question goes to a language model, which answers from what it
                  absorbed during training. The section numbers it produces are
                  generated text like any other text — which means they can be
                  fluent, confident, and entirely invented.
                </p>
                <p className="text-sm text-rose-900/70">
                  If the model is wrong, nothing in the system is positioned to
                  notice.
                </p>
              </div>

              <div className="rounded-3xl border border-emerald-200 bg-emerald-50/50 p-8">
                <p className="mb-4 inline-flex rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold tracking-wide text-emerald-800 uppercase">
                  This design
                </p>
                <h2 className="mb-4 font-serif text-2xl font-semibold text-slate-900">
                  The corpus is the source
                </h2>
                <p className="mb-5 text-[15px] leading-relaxed text-gray-700">
                  Retrieval finds the actual passage first. The model, if one is
                  configured at all, is given that passage and asked only to
                  express it readably. It is never asked what the law is.
                </p>
                <p className="text-sm text-emerald-900/70">
                  The last fallback needs no model at all: the answer is composed
                  from the retrieved text itself.
                </p>
              </div>
            </div>
          </Reveal>
        </div>
      </section>

      {/* ═══ RETRIEVAL LAYERS ═══ */}
      <section className="border-y border-gray-100 bg-gray-50/60 px-6 py-24">
        <div className="mx-auto max-w-5xl">
          <Reveal as="header" className="mx-auto mb-14 max-w-2xl text-center">
            <h2 className="mb-5 font-serif text-4xl font-bold tracking-tight md:text-5xl">
              Three ways of finding the same passage
            </h2>
            <p className="text-lg leading-relaxed text-gray-600">
              Hybrid retrieval, because no single method survives contact with
              eight languages and a vocabulary as exact as statute.
            </p>
          </Reveal>

          <div className="space-y-4">
            {LAYERS.map((layer, i) => (
              <Reveal key={layer.name} delay={i * 0.08} from="left">
                <div className="lift flex flex-col gap-5 rounded-3xl border border-gray-200 bg-white p-8 sm:flex-row sm:items-start hover:border-amber-300">
                  <span className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-slate-900 text-white">
                    <layer.icon className="h-5 w-5" aria-hidden="true" />
                  </span>
                  <div>
                    <h3 className="mb-2 font-serif text-xl font-semibold">
                      {layer.name}
                    </h3>
                    <p className="text-[15px] leading-relaxed text-gray-600">
                      {layer.body}
                    </p>
                  </div>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ REFUSING ═══ */}
      <section className="px-6 py-24">
        <div className="mx-auto max-w-4xl">
          <Reveal as="header" className="mb-12 text-center">
            <span className="mb-5 inline-flex h-14 w-14 items-center justify-center rounded-2xl bg-amber-100 text-amber-700">
              <Filter className="h-6 w-6" aria-hidden="true" />
            </span>
            <h2 className="mb-5 font-serif text-4xl font-bold tracking-tight md:text-5xl">
              Refusing to answer is a feature
            </h2>
            <p className="text-lg leading-relaxed text-gray-600">
              Several guards have to agree before an answer is produced at all.
              For a legal tool, a confident wrong answer is worse than no answer,
              because the person acts on it.
            </p>
          </Reveal>

          <Reveal delay={0.1}>
            <div className="rounded-3xl border border-gray-200 bg-slate-950 p-8 text-slate-200 md:p-12">
              <div className="mb-8 flex items-start gap-4">
                <Quote className="h-8 w-8 shrink-0 text-amber-400/60" aria-hidden="true" />
                <p className="font-serif text-xl leading-relaxed text-white italic md:text-2xl">
                  The extractive path cannot invent a section number, because it
                  never writes one.
                </p>
              </div>
              <dl className="grid gap-6 border-t border-white/10 pt-8 sm:grid-cols-3">
                <div>
                  <dd className="mb-1.5 font-mono text-3xl font-bold text-amber-400">
                    <CountUp value={EVAL_STATS.questions.value} />
                  </dd>
                  <dt className="text-xs text-slate-400">
                    Questions in the evaluation set
                  </dt>
                </div>
                <div>
                  <dd className="mb-1.5 font-mono text-3xl font-bold text-amber-400">
                    <CountUp
                      value={EVAL_STATS.hitAt1.value}
                      decimals={EVAL_STATS.hitAt1.decimals}
                      suffix="%"
                    />
                  </dd>
                  <dt className="text-xs text-slate-400">
                    Correct provision ranked first
                  </dt>
                </div>
                <div>
                  <dd className="mb-1.5 font-mono text-3xl font-bold text-amber-400">
                    <CountUp value={14} />
                    <span className="text-lg text-amber-400/60">/14</span>
                  </dd>
                  <dt className="text-xs text-slate-400">
                    Guard-set questions correctly refused
                  </dt>
                </div>
              </dl>
              <p className="mt-8 text-sm leading-relaxed text-slate-400">
                The evaluation also reports where the guards still fail — three
                out-of-scope questions about recruitment exams are currently
                answered when they should be refused. That is published on the{" "}
                <Link
                  href="/disclaimer"
                  transitionTypes={["nav-forward"]}
                  className="font-medium text-amber-400 underline underline-offset-4 hover:text-amber-300"
                >
                  disclaimer page
                </Link>{" "}
                rather than hidden.
              </p>
            </div>
          </Reveal>
        </div>
      </section>

      {/* ═══ CROSS-LINGUAL ═══ */}
      <section className="border-y border-gray-100 bg-amber-50/40 px-6 py-24">
        <div className="mx-auto max-w-4xl">
          <Reveal as="header" className="mb-12 text-center">
            <h2 className="mb-5 font-serif text-4xl font-bold tracking-tight md:text-5xl">
              Why the languages are scored separately
            </h2>
            <p className="mx-auto max-w-2xl text-lg leading-relaxed text-gray-600">
              If you average English and Indic results together, English
              dominates and an Indic failure disappears into the mean. Reporting
              them apart has caught regressions that every English metric stayed
              green through.
            </p>
          </Reveal>

          <Reveal delay={0.1}>
            <div className="grid gap-4 sm:grid-cols-3">
              {CROSS_LINGUAL_FIGURES.map((stat) => (
                <div
                  key={stat.label}
                  className="lift rounded-3xl border border-amber-200 bg-white p-7 text-center hover:border-amber-400"
                >
                  <div className="mb-2 font-serif text-4xl font-bold text-amber-700">
                    <CountUp value={stat.value} suffix={stat.suffix} />
                  </div>
                  <div className="text-sm leading-relaxed text-gray-600">
                    {stat.label}
                  </div>
                </div>
              ))}
            </div>
          </Reveal>
        </div>
      </section>

      {/* ═══ THE TOOLKIT PATH ═══ */}
      <section className="px-6 py-24">
        <div className="mx-auto max-w-4xl">
          <Reveal as="header" className="mb-12 text-center">
            <span className="mb-5 inline-flex h-14 w-14 items-center justify-center rounded-2xl bg-slate-900 text-white">
              <ShieldCheck className="h-6 w-6" aria-hidden="true" />
            </span>
            <h2 className="mb-5 font-serif text-4xl font-bold tracking-tight md:text-5xl">
              The toolkit never calls a model at all
            </h2>
            <p className="text-lg leading-relaxed text-gray-600">
              Deadlines, forums, fees, stamp duty and document drafting are
              lookup tables and calendar arithmetic. For something that tells a
              person whether they still have the right to sue, being identical
              every time matters more than being eloquent.
            </p>
          </Reveal>

          <Reveal delay={0.1}>
            <div className="flex flex-col gap-5 rounded-3xl border border-gray-200 bg-gray-50 p-8 sm:flex-row sm:items-start">
              <span className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-white text-slate-900 shadow-sm">
                <WifiOff className="h-5 w-5" aria-hidden="true" />
              </span>
              <div>
                <h3 className="mb-2 font-serif text-xl font-semibold">
                  Which is why the deadline calculator works offline
                </h3>
                <p className="text-[15px] leading-relaxed text-gray-600">
                  The lookup tables are sent to the browser and the arithmetic
                  repeated there. The duplication is kept honest by a parity
                  check that runs every rule through both implementations and
                  fails if they ever disagree.
                </p>
              </div>
            </div>
          </Reveal>
        </div>
      </section>

      {/* ═══ CTA ═══ */}
      <section className="px-6 pb-24">
        <Reveal>
          <div className="mx-auto max-w-4xl rounded-[2.5rem] border border-gray-200 bg-gradient-to-br from-gray-50 to-white p-12 text-center md:p-16">
            <BookOpen className="mx-auto mb-6 h-10 w-10 text-amber-600" aria-hidden="true" />
            <h2 className="mb-5 font-serif text-3xl font-bold tracking-tight text-balance md:text-4xl">
              Everything here is checkable
            </h2>
            <p className="mx-auto mb-9 max-w-xl text-lg leading-relaxed text-gray-600">
              The corpus, the retrieval code and the evaluation that gates every
              change to them are all public. So is this page&rsquo;s arithmetic.
            </p>
            <div className="flex flex-wrap items-center justify-center gap-3">
              <Link
                href="/toolkit"
                transitionTypes={["nav-forward"]}
                className="lift inline-flex items-center gap-2 rounded-full bg-slate-900 px-8 py-4 text-base font-medium text-white hover:bg-slate-800"
              >
                Try the toolkit
                <ArrowRight className="h-4 w-4" aria-hidden="true" />
              </Link>
              <Link
                href="/about"
                transitionTypes={["nav-forward"]}
                className="lift inline-flex items-center gap-2 rounded-full border border-gray-300 bg-white px-8 py-4 text-base font-medium text-slate-900 hover:border-slate-400"
              >
                About the project
              </Link>
            </div>
          </div>
        </Reveal>
      </section>
    </div>
  );
}
