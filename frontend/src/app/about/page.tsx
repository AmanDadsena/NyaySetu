import type { Metadata } from "next";
import Link from "next/link";
import {
  ArrowRight,
  BookOpen,
  ClipboardCheck,
  Eye,
  Scale,
  Shield,
  Users,
  Zap,
} from "lucide-react";
import { Reveal } from "@/components/motion/Reveal";
import { CountUp } from "@/components/motion/CountUp";
import { CORPUS_STATS, EVAL_STATS, type SiteStat } from "@/lib/site-stats";

/* Annotated so the optional `decimals`/`suffix` stay reachable — the inferred
   union of these heterogeneous entries would drop them. */
const HEADLINE_FIGURES: SiteStat[] = [
  CORPUS_STATS.passages,
  CORPUS_STATS.acts,
  CORPUS_STATS.languages,
  EVAL_STATS.hitAt1,
];

export const metadata: Metadata = {
  title: "About — Nyaysetu",
  description:
    "Why Nyaysetu answers from cited statute rather than from a model's memory, and the principles the project is built on.",
};

/**
 * About page.
 *
 * The stats band here used to open with "1.4B+ — Citizens We Serve", which was
 * India's population relabelled as a userbase. It has been replaced with the
 * project's actual measurements, and the page now explains the thinking behind
 * the architecture rather than asserting scale it does not have.
 */

const PRINCIPLES = [
  {
    icon: BookOpen,
    title: "Cite or say nothing",
    body: "Every answer names the Act and the section it rests on and shows the passage it was built from. An answer nobody can check is not useful in a legal context — it is just confident text.",
  },
  {
    icon: Shield,
    title: "Refusing is a valid answer",
    body: "Several guards have to agree before the assistant answers at all. Deciding a question is out of corpus is treated as success, not failure, because someone acts on what they read here.",
  },
  {
    icon: ClipboardCheck,
    title: "Measure, do not assert",
    body: "A single evaluation gates every change to the corpus, the lexicon or the retriever, and exits non-zero on regression. Claims about quality are reproducible by running one command.",
  },
  {
    icon: Users,
    title: "The language people actually think in",
    body: "Eight languages, with cross-lingual retrieval scored separately so an Indic failure cannot hide inside an English-dominated average.",
  },
  {
    icon: Eye,
    title: "Publish the flaws",
    body: "Where the evaluation shows the tool still gets things wrong, that is written on the disclaimer page rather than left for a user to discover at their own cost.",
  },
  {
    icon: Zap,
    title: "Work without an account, and without a network",
    body: "The assistant and the whole toolkit run signed out. The deadline calculator keeps working offline, because the people who need it most have the least reliable connections.",
  },
] as const;

const FRAMEWORKS = [
  {
    tone: "amber",
    icon: Scale,
    title: "Constitution of India",
    body: "The supreme law, adopted in 1949 and in force since 1950. It guarantees Fundamental Rights and sets out the framework of powers and duties for every institution of the State.",
    href: "https://legislative.gov.in/constitution-of-india",
    cta: "Read the official text",
  },
  {
    tone: "blue",
    icon: Shield,
    title: "Bharatiya Nyaya Sanhita, 2023",
    body: "India's criminal code since 1 July 2024, replacing the Indian Penal Code of 1860. It groups offences against women and children into a single chapter and introduces community service as a punishment.",
    href: "https://www.indiacode.nic.in/handle/123456789/21238",
    cta: "Open on India Code",
  },
  {
    tone: "emerald",
    icon: Users,
    title: "Legal Services Authorities Act, 1987",
    body: "The statute that makes free legal aid a right rather than a favour. Section 12 lists who qualifies — a wider list than most people assume, covering every woman and child regardless of income.",
    href: "https://nalsa.gov.in",
    cta: "Visit NALSA",
  },
] as const;

const TONES = {
  amber: "bg-amber-50/60 border-amber-100 text-amber-700 bg-amber-100",
  blue: "bg-blue-50/60 border-blue-100 text-blue-700 bg-blue-100",
  emerald: "bg-emerald-50/60 border-emerald-100 text-emerald-700 bg-emerald-100",
} as const;

export default function AboutPage() {
  return (
    <div className="bg-white">
      {/* ═══ HERO ═══ */}
      <section className="relative overflow-hidden border-b border-gray-100 px-6 pt-20 pb-20">
        <div aria-hidden="true" className="pointer-events-none absolute inset-0 -z-10">
          <div className="animate-aurora absolute -top-40 left-1/4 h-[30rem] w-[30rem] rounded-full bg-amber-200/30 blur-3xl" />
          <div className="animate-aurora absolute -top-16 right-0 h-[26rem] w-[26rem] rounded-full bg-violet-200/25 blur-3xl [animation-delay:-11s]" />
        </div>

        <div className="mx-auto max-w-3xl text-center">
          <p className="animate-fade-in-up mb-5 text-sm font-semibold tracking-[0.12em] text-amber-700 uppercase">
            About
          </p>
          <h1
            className="animate-fade-in-up mb-6 font-serif text-5xl leading-tight font-bold tracking-tight text-balance md:text-6xl"
            style={{ animationDelay: "0.08s" }}
          >
            Most people never find out what the law already gives them
          </h1>
          <p
            className="animate-fade-in-up text-lg leading-relaxed text-gray-600 md:text-xl"
            style={{ animationDelay: "0.16s" }}
          >
            Not because the information is secret — it is all published — but
            because it is written in a register most people cannot read, in a
            language many do not speak, and scattered across portals that assume
            you already know which Act applies. Nyaysetu is an attempt at the
            bridge.
          </p>
        </div>
      </section>

      {/* ═══ REAL NUMBERS ═══ */}
      <section className="px-6 py-20">
        <div className="mx-auto max-w-5xl">
          <Reveal>
            <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
              {HEADLINE_FIGURES.map((stat) => (
                <div
                  key={stat.label}
                  className="lift rounded-3xl border border-gray-200 bg-gradient-to-br from-white to-gray-50 p-7 text-center hover:border-slate-300"
                >
                  <div className="mb-2 font-serif text-4xl font-bold text-slate-900">
                    <CountUp
                      value={stat.value}
                      decimals={stat.decimals}
                      suffix={stat.suffix}
                    />
                  </div>
                  <div className="text-sm leading-relaxed text-gray-500">
                    {stat.label}
                  </div>
                </div>
              ))}
            </div>
          </Reveal>
          <Reveal delay={0.1}>
            <p className="mt-6 text-center text-sm text-gray-400">
              Every figure on this site is reproducible from the repository.
              None of them describe a userbase, because the project does not
              claim one.
            </p>
          </Reveal>
        </div>
      </section>

      {/* ═══ PRINCIPLES ═══ */}
      <section className="border-y border-gray-100 bg-gray-50/60 px-6 py-24">
        <div className="mx-auto max-w-6xl">
          <Reveal as="header" className="mx-auto mb-16 max-w-2xl text-center">
            <h2 className="mb-5 font-serif text-4xl font-bold tracking-tight md:text-5xl">
              What the project holds to
            </h2>
            <p className="text-lg leading-relaxed text-gray-600">
              Six decisions that shaped everything else, and that a contributor
              is expected to keep.
            </p>
          </Reveal>

          <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
            {PRINCIPLES.map((p, i) => (
              <Reveal key={p.title} delay={(i % 3) * 0.08}>
                <div className="lift h-full rounded-3xl border border-gray-200 bg-white p-8 hover:border-amber-300 hover:shadow-lg">
                  <span className="mb-5 flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-900 text-white">
                    <p.icon className="h-5 w-5" aria-hidden="true" />
                  </span>
                  <h3 className="mb-3 font-serif text-xl font-semibold">
                    {p.title}
                  </h3>
                  <p className="text-[15px] leading-relaxed text-gray-600">
                    {p.body}
                  </p>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ FRAMEWORKS ═══ */}
      <section className="px-6 py-24">
        <div className="mx-auto max-w-6xl">
          <Reveal as="header" className="mx-auto mb-16 max-w-2xl text-center">
            <h2 className="mb-5 font-serif text-4xl font-bold tracking-tight md:text-5xl">
              The statutes this rests on
            </h2>
            <p className="text-lg leading-relaxed text-gray-600">
              Everything in the corpus traces to an official source. These three
              carry most of the weight.
            </p>
          </Reveal>

          <div className="grid gap-6 lg:grid-cols-3">
            {FRAMEWORKS.map((f, i) => {
              const [bg, border, text, iconBg] = TONES[f.tone].split(" ");
              return (
                <Reveal key={f.title} delay={i * 0.1}>
                  <div
                    className={`lift flex h-full flex-col rounded-3xl border p-8 ${bg} ${border}`}
                  >
                    <span
                      className={`mb-6 flex h-12 w-12 items-center justify-center rounded-2xl ${iconBg} ${text}`}
                    >
                      <f.icon className="h-6 w-6" aria-hidden="true" />
                    </span>
                    <h3 className="mb-4 font-serif text-2xl font-semibold text-slate-900">
                      {f.title}
                    </h3>
                    <p className="mb-8 flex-1 text-[15px] leading-relaxed text-gray-700">
                      {f.body}
                    </p>
                    <a
                      href={f.href}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex w-fit items-center gap-2 rounded-full bg-slate-900 px-5 py-2.5 text-sm font-medium text-white transition-colors hover:bg-slate-800"
                    >
                      {f.cta}
                      <ArrowRight className="h-4 w-4" aria-hidden="true" />
                    </a>
                  </div>
                </Reveal>
              );
            })}
          </div>
        </div>
      </section>

      {/* ═══ HONESTY ═══ */}
      <section className="border-t border-gray-100 bg-slate-950 px-6 py-24 text-slate-300">
        <div className="mx-auto max-w-3xl text-center">
          <Reveal>
            <Scale className="mx-auto mb-8 h-12 w-12 text-amber-500" aria-hidden="true" />
            <h2 className="mb-6 font-serif text-3xl font-semibold text-balance text-amber-50 md:text-4xl">
              What this project will not do
            </h2>
            <p className="mb-8 text-lg leading-relaxed text-slate-300">
              It will not tell you what a court will decide, read your documents,
              or stand in for an advocate who has heard your facts. It gives
              legal information, and it shows its working so you can check it.
            </p>
            <p className="mb-10 leading-relaxed text-slate-400">
              Where the evaluation shows it still gets things wrong, that is
              written down and published rather than quietly fixed in the
              marketing copy.
            </p>
            <div className="flex flex-wrap items-center justify-center gap-3">
              <Link
                href="/how-it-works"
                transitionTypes={["nav-forward"]}
                className="lift inline-flex items-center gap-2 rounded-full bg-amber-400 px-7 py-3.5 text-base font-medium text-slate-950 hover:bg-amber-300"
              >
                How it works
                <ArrowRight className="h-4 w-4" aria-hidden="true" />
              </Link>
              <Link
                href="/disclaimer"
                transitionTypes={["nav-forward"]}
                className="lift inline-flex items-center gap-2 rounded-full border border-white/20 px-7 py-3.5 text-base font-medium text-white hover:border-white/40"
              >
                Read the known limits
              </Link>
            </div>
          </Reveal>
        </div>
      </section>
    </div>
  );
}
