"use client";

/**
 * Knowledge base.
 *
 * Reference reading rather than a product pitch: the parts of Indian law people
 * most often need and least often find stated plainly. Expanded from four thin
 * tabs to five substantial ones.
 *
 * Two editorial rules. Nothing is asserted that cannot be traced to a statute
 * or a reported judgment, and where a provision has been struck down or
 * replaced that is stated rather than quietly omitted — Section 66A of the IT
 * Act is the clearest example, and it is still widely cited by people who do
 * not know it has been void since 2015.
 */

import { useState } from "react";
import Link from "next/link";
import {
  ArrowUpRight,
  Award,
  BookOpen,
  Gavel,
  Globe,
  Landmark,
  Scale,
  ShieldAlert,
  Users,
} from "lucide-react";
import { Reveal } from "@/components/motion/Reveal";
import { cn } from "@/lib/utils";

type SectionId = "constitution" | "bns" | "landmark" | "cyber" | "everyday";

const TABS: { id: SectionId; label: string; icon: typeof Scale }[] = [
  { id: "constitution", label: "Constitution", icon: Scale },
  { id: "bns", label: "BNS 2023", icon: BookOpen },
  { id: "landmark", label: "Landmark judgments", icon: Award },
  { id: "cyber", label: "Cyber & data", icon: Globe },
  { id: "everyday", label: "Everyday rights", icon: Users },
];

const FUNDAMENTAL_RIGHTS = [
  {
    articles: "Articles 14–18",
    name: "Right to Equality",
    body: "Equality before the law and equal protection of the laws. Prohibits discrimination on grounds of religion, race, caste, sex or place of birth, guarantees equality of opportunity in public employment, and abolishes untouchability and titles.",
  },
  {
    articles: "Articles 19–22",
    name: "Right to Freedom",
    body: "Six freedoms including speech and expression, assembly, association, movement and profession — each subject to reasonable restrictions. Also protects against conviction under retrospective laws, double jeopardy and self-incrimination, and guarantees life and personal liberty.",
  },
  {
    articles: "Articles 23–24",
    name: "Right against Exploitation",
    body: "Prohibits trafficking in human beings, begar and other forms of forced labour, and bars employment of children below fourteen in factories, mines or other hazardous work.",
  },
  {
    articles: "Articles 25–28",
    name: "Right to Freedom of Religion",
    body: "Freedom of conscience and the right to profess, practise and propagate religion, the right of religious denominations to manage their own affairs, and freedom from compelled religious taxation or instruction.",
  },
  {
    articles: "Articles 29–30",
    name: "Cultural and Educational Rights",
    body: "Protects the language, script and culture of minorities, and their right to establish and administer educational institutions of their choice.",
  },
  {
    articles: "Article 32",
    name: "Right to Constitutional Remedies",
    body: "The right to move the Supreme Court directly to enforce the rights above. Ambedkar called it the heart and soul of the Constitution — a right that cannot be enforced is not a right.",
  },
] as const;

const JUDGMENTS = [
  {
    year: "1973",
    name: "Kesavananda Bharati v. State of Kerala",
    holding: "Basic Structure doctrine",
    body: "A thirteen-judge bench — still the largest ever assembled — held that Parliament may amend any part of the Constitution but cannot alter its basic structure. Features such as judicial review, secularism, federalism and the separation of powers are beyond the amending power.",
  },
  {
    year: "1978",
    name: "Maneka Gandhi v. Union of India",
    holding: "Article 21 transformed",
    body: "A procedure depriving someone of life or personal liberty must be just, fair and reasonable, not merely a procedure that happens to be written into law. This opened Article 21 to a long line of derived rights, from livelihood and shelter to a clean environment.",
  },
  {
    year: "1992",
    name: "Indra Sawhney v. Union of India",
    holding: "The 50% ceiling on reservation",
    body: "Upheld reservation for Other Backward Classes in public employment while capping total reservation at fifty per cent except in extraordinary circumstances, and excluding the 'creamy layer' from its benefit.",
  },
  {
    year: "1997",
    name: "Vishaka v. State of Rajasthan",
    holding: "Workplace harassment guidelines",
    body: "In the absence of legislation, the Court laid down binding guidelines against sexual harassment at work, drawing on India's international obligations. These governed for sixteen years until the 2013 Act replaced them.",
  },
  {
    year: "2015",
    name: "Shreya Singhal v. Union of India",
    holding: "Section 66A struck down",
    body: "Struck down Section 66A of the IT Act — which criminalised 'grossly offensive' online messages — as unconstitutionally vague and a disproportionate restriction on free speech. Despite this, cases were still being registered under it years later.",
  },
  {
    year: "2017",
    name: "K.S. Puttaswamy (Retd.) v. Union of India",
    holding: "Right to Privacy",
    body: "A unanimous nine-judge bench held privacy to be a fundamental right intrinsic to life and personal liberty under Article 21. The foundation of Indian data protection law, and of the limits on state surveillance.",
  },
] as const;

const CYBER = [
  {
    section: "Section 43A",
    name: "Compensation for data leaks",
    body: "A body corporate handling sensitive personal data that is negligent in maintaining reasonable security practices, causing wrongful loss or gain, is liable to pay compensation to the person affected.",
  },
  {
    section: "Section 66C",
    name: "Identity theft",
    body: "Fraudulent or dishonest use of another person's electronic signature, password or unique identification feature. Punishable with imprisonment up to three years and a fine.",
  },
  {
    section: "Section 66D",
    name: "Cheating by personation",
    body: "Cheating by pretending to be someone else using a computer resource — the provision most online financial frauds are charged under.",
  },
  {
    section: "Section 67",
    name: "Obscene material",
    body: "Publishing or transmitting obscene material in electronic form. Sections 67A and 67B deal with sexually explicit material and with material depicting children, which carry substantially higher punishment.",
  },
] as const;

const EVERYDAY = [
  {
    icon: ShieldAlert,
    title: "If you are arrested",
    body: "You must be told the grounds of arrest, may consult a lawyer of your choice, and must be produced before a Magistrate within twenty-four hours excluding travel time. If you cannot afford a lawyer, the State must provide one.",
    cite: "Constitution Articles 20–22; BNSS Sections 47 and 58",
  },
  {
    icon: Gavel,
    title: "If the police will not register your FIR",
    body: "Send the complaint in writing by registered post to the Superintendent of Police, who must investigate if it discloses a cognizable offence. If that fails, apply to the Judicial Magistrate, who can direct an investigation.",
    cite: "BNSS Sections 173(4) and 175(3)",
  },
  {
    icon: Users,
    title: "Free legal aid",
    body: "A statutory entitlement, not charity. Every woman and every child qualifies regardless of income, as do members of Scheduled Castes and Scheduled Tribes, persons with disabilities, people in custody, and anyone below their State's income limit.",
    cite: "Legal Services Authorities Act, 1987 — Section 12",
  },
  {
    icon: BookOpen,
    title: "Asking the government for information",
    body: "Any citizen may request information from a public authority, which must normally reply within thirty days — or within forty-eight hours where life or liberty is concerned. The fee is nominal and waived entirely for people below the poverty line.",
    cite: "Right to Information Act, 2005",
  },
] as const;

export default function KnowledgeBase() {
  const [active, setActive] = useState<SectionId>("constitution");

  return (
    <div className="bg-white pb-24">
      {/* ═══ HERO ═══ */}
      <section className="relative overflow-hidden border-b border-gray-100 px-6 pt-20 pb-14">
        <div aria-hidden="true" className="pointer-events-none absolute inset-0 -z-10">
          <div className="animate-aurora absolute -top-40 left-1/3 h-[30rem] w-[30rem] rounded-full bg-amber-200/35 blur-3xl" />
        </div>
        <div className="mx-auto max-w-3xl text-center">
          <div className="animate-fade-in-up mb-6 inline-flex items-center gap-2 rounded-full border border-amber-200 bg-amber-50/70 px-4 py-1.5 text-sm font-medium text-amber-900">
            <Landmark className="h-4 w-4" aria-hidden="true" />
            Reference reading
          </div>
          <h1
            className="animate-fade-in-up mb-5 font-serif text-5xl font-bold tracking-tight text-balance text-slate-900 md:text-6xl"
            style={{ animationDelay: "0.08s" }}
          >
            Indian legal <span className="text-amber-600">knowledge base</span>
          </h1>
          <p
            className="animate-fade-in-up text-lg leading-relaxed text-gray-600"
            style={{ animationDelay: "0.16s" }}
          >
            The parts of the law people most often need and least often find
            written plainly — the Constitution&rsquo;s guarantees, the new
            criminal code, the judgments that shaped both, and what to do on an
            ordinary bad day.
          </p>
        </div>
      </section>

      {/* ═══ TABS ═══ */}
      <div className="sticky top-[73px] z-30 border-b border-gray-100 bg-white/85 backdrop-blur-xl">
        <div
          role="tablist"
          aria-label="Knowledge base sections"
          className="mx-auto flex max-w-5xl gap-1 overflow-x-auto px-4 py-3"
        >
          {TABS.map((t) => (
            <button
              key={t.id}
              role="tab"
              aria-selected={active === t.id}
              onClick={() => setActive(t.id)}
              className={cn(
                "flex shrink-0 items-center gap-2 rounded-xl px-4 py-2.5 text-sm font-medium transition-all",
                active === t.id
                  ? "bg-slate-900 text-white shadow-sm"
                  : "text-gray-600 hover:bg-gray-100 hover:text-slate-900",
              )}
            >
              <t.icon className="h-4 w-4" aria-hidden="true" />
              {t.label}
            </button>
          ))}
        </div>
      </div>

      <main className="mx-auto max-w-5xl px-6 py-14">
        {/* ── CONSTITUTION ── */}
        {active === "constitution" && (
          <div className="space-y-8">
            <Reveal>
              <div className="relative overflow-hidden rounded-[2rem] bg-slate-950 p-8 text-white md:p-12">
                <Landmark
                  className="pointer-events-none absolute -top-8 -right-8 h-64 w-64 opacity-[0.06]"
                  aria-hidden="true"
                />
                <div className="relative">
                  <h2 className="mb-4 font-serif text-3xl font-bold text-amber-400">
                    Fundamental Rights
                  </h2>
                  <p className="max-w-3xl text-lg leading-relaxed text-slate-300">
                    Part III, Articles 12–35. These are enforceable against the
                    State: a law inconsistent with them is void to the extent of
                    the inconsistency (Article 13), and you can go straight to
                    the Supreme Court to enforce them (Article 32).
                  </p>
                </div>
              </div>
            </Reveal>

            <div className="grid gap-4 md:grid-cols-2">
              {FUNDAMENTAL_RIGHTS.map((r, i) => (
                <Reveal key={r.name} delay={(i % 2) * 0.08}>
                  <div className="lift h-full rounded-2xl border border-gray-200 bg-white p-6 hover:border-amber-300">
                    <p className="mb-2 font-mono text-xs font-semibold tracking-wide text-amber-700 uppercase">
                      {r.articles}
                    </p>
                    <h3 className="mb-3 font-serif text-xl font-semibold text-slate-900">
                      {r.name}
                    </h3>
                    <p className="text-sm leading-relaxed text-gray-600">{r.body}</p>
                  </div>
                </Reveal>
              ))}
            </div>

            <Reveal delay={0.1}>
              <div className="grid gap-4 md:grid-cols-2">
                <div className="rounded-2xl border border-gray-200 bg-gray-50 p-6">
                  <h3 className="mb-3 font-serif text-lg font-semibold text-slate-900">
                    Directive Principles (Part IV)
                  </h3>
                  <p className="text-sm leading-relaxed text-gray-600">
                    Goals for the State — a living wage, free legal aid, equal
                    justice, public health. Not enforceable in court, but
                    Article 37 makes them fundamental to governance, and courts
                    routinely read them alongside Fundamental Rights.
                  </p>
                </div>
                <div className="rounded-2xl border border-gray-200 bg-gray-50 p-6">
                  <h3 className="mb-3 font-serif text-lg font-semibold text-slate-900">
                    Fundamental Duties (Part IVA)
                  </h3>
                  <p className="text-sm leading-relaxed text-gray-600">
                    Eleven duties added by the 42nd Amendment in 1976, from
                    abiding by the Constitution to protecting the environment
                    and providing education to one&rsquo;s children.
                  </p>
                </div>
              </div>
            </Reveal>
          </div>
        )}

        {/* ── BNS ── */}
        {active === "bns" && (
          <div className="space-y-8">
            <Reveal>
              <div className="rounded-[2rem] border border-gray-200 bg-white p-8 shadow-sm md:p-12">
                <h2 className="mb-4 font-serif text-3xl font-bold text-slate-900">
                  Bharatiya Nyaya Sanhita, 2023
                </h2>
                <p className="mb-8 max-w-3xl text-lg leading-relaxed text-gray-600">
                  India&rsquo;s penal code since 1 July 2024, replacing the
                  Indian Penal Code of 1860. It arrived alongside two companion
                  statutes, and together the three replaced the colonial
                  framework that governed Indian criminal law for over a century.
                </p>
                <div className="grid gap-4 sm:grid-cols-3">
                  {[
                    { n: "Bharatiya Nyaya Sanhita", d: "The offences and their punishments. Replaces the IPC, 1860.", c: "358 sections" },
                    { n: "Bharatiya Nagarik Suraksha Sanhita", d: "Procedure — arrest, investigation, trial, bail. Replaces the CrPC, 1973.", c: "531 sections" },
                    { n: "Bharatiya Sakshya Adhiniyam", d: "Evidence, including electronic records. Replaces the Evidence Act, 1872.", c: "170 sections" },
                  ].map((s) => (
                    <div key={s.n} className="rounded-2xl border border-slate-100 bg-slate-50 p-5">
                      <h3 className="mb-2 font-semibold text-slate-900">{s.n}</h3>
                      <p className="mb-3 text-sm leading-relaxed text-gray-600">{s.d}</p>
                      <span className="inline-block rounded-full bg-white px-3 py-1 font-mono text-xs text-slate-600">
                        {s.c}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </Reveal>

            <div className="grid gap-4 md:grid-cols-3">
              {[
                { t: "Offences against women and children", b: "Previously scattered across the IPC, now consolidated into a single chapter placed early in the code — a deliberate signal of priority." },
                { t: "Community service", b: "Introduced as a punishment for certain minor offences, the first time Indian criminal law has recognised a non-custodial, non-monetary penalty of this kind." },
                { t: "Organised crime and terrorism", b: "Defined within the general penal code for the first time, rather than existing only in special legislation." },
              ].map((item, i) => (
                <Reveal key={item.t} delay={i * 0.08}>
                  <div className="lift h-full rounded-2xl border border-blue-100 bg-blue-50/50 p-6 hover:border-blue-300">
                    <h3 className="mb-3 font-serif text-lg font-semibold text-slate-900">
                      {item.t}
                    </h3>
                    <p className="text-sm leading-relaxed text-gray-700">{item.b}</p>
                  </div>
                </Reveal>
              ))}
            </div>

            <Reveal delay={0.1}>
              <div className="rounded-2xl border border-amber-200 bg-amber-50/60 p-6">
                <p className="text-sm leading-relaxed text-amber-950">
                  <strong className="font-semibold">A practical note.</strong>{" "}
                  Offences committed before 1 July 2024 continue to be tried
                  under the IPC. For some years yet, both codes are live and the
                  section number that applies depends on the date of the
                  offence, not the date of the case.
                </p>
              </div>
            </Reveal>
          </div>
        )}

        {/* ── LANDMARK ── */}
        {active === "landmark" && (
          <div className="space-y-4">
            <Reveal as="header" className="mb-8">
              <h2 className="mb-3 font-serif text-3xl font-bold text-slate-900">
                Landmark Supreme Court judgments
              </h2>
              <p className="max-w-3xl text-lg leading-relaxed text-gray-600">
                Six decisions that changed what the Constitution means in
                practice.
              </p>
            </Reveal>

            {JUDGMENTS.map((j, i) => (
              <Reveal key={j.name} delay={(i % 3) * 0.06} from="left">
                <article className="lift rounded-2xl border border-gray-200 bg-white p-7 hover:border-amber-300 hover:shadow-md">
                  <div className="mb-3 flex flex-wrap items-baseline gap-x-4 gap-y-1">
                    <span className="font-mono text-2xl font-bold text-amber-600">
                      {j.year}
                    </span>
                    <h3 className="font-serif text-xl font-semibold text-slate-900">
                      {j.name}
                    </h3>
                  </div>
                  <p className="mb-3 inline-block rounded-full bg-amber-50 px-3 py-1 text-xs font-semibold tracking-wide text-amber-800 uppercase">
                    {j.holding}
                  </p>
                  <p className="text-[15px] leading-relaxed text-gray-600">{j.body}</p>
                </article>
              </Reveal>
            ))}
          </div>
        )}

        {/* ── CYBER ── */}
        {active === "cyber" && (
          <div className="space-y-8">
            <Reveal>
              <div className="rounded-[2rem] bg-slate-950 p-8 text-white md:p-12">
                <h2 className="mb-4 font-serif text-3xl font-bold text-emerald-400">
                  Information Technology Act, 2000
                </h2>
                <p className="max-w-3xl text-lg leading-relaxed text-slate-300">
                  The primary law on cybercrime and electronic commerce. It gives
                  legal recognition to electronic records and digital signatures,
                  and defines the offences most online frauds are charged under.
                </p>
              </div>
            </Reveal>

            <div className="grid gap-4 md:grid-cols-2">
              {CYBER.map((c, i) => (
                <Reveal key={c.section} delay={(i % 2) * 0.08}>
                  <div className="lift h-full rounded-2xl border border-gray-200 bg-white p-6 hover:border-emerald-300">
                    <p className="mb-2 font-mono text-xs font-semibold tracking-wide text-emerald-700 uppercase">
                      {c.section}
                    </p>
                    <h3 className="mb-3 font-serif text-lg font-semibold text-slate-900">
                      {c.name}
                    </h3>
                    <p className="text-sm leading-relaxed text-gray-600">{c.body}</p>
                  </div>
                </Reveal>
              ))}
            </div>

            <Reveal delay={0.1}>
              <div className="rounded-2xl border border-rose-200 bg-rose-50/60 p-6">
                <h3 className="mb-3 font-serif text-lg font-semibold text-rose-950">
                  Section 66A no longer exists
                </h3>
                <p className="text-sm leading-relaxed text-rose-900/90">
                  It was struck down as unconstitutional in{" "}
                  <em>Shreya Singhal v. Union of India</em> (2015). It is
                  mentioned here because it is still widely quoted, and cases
                  continued to be registered under it for years afterwards. No
                  one can lawfully be charged under Section 66A.
                </p>
              </div>
            </Reveal>

            <Reveal delay={0.15}>
              <div className="rounded-2xl border border-gray-200 bg-gray-50 p-6">
                <h3 className="mb-3 font-serif text-lg font-semibold text-slate-900">
                  Digital Personal Data Protection Act, 2023
                </h3>
                <p className="mb-4 text-sm leading-relaxed text-gray-600">
                  India&rsquo;s dedicated data protection statute, enacted in the
                  wake of <em>Puttaswamy</em>. It builds obligations around
                  consent, purpose limitation and breach notification, and gives
                  individuals rights of access, correction and erasure.
                </p>
                <p className="text-sm text-gray-500">
                  Its provisions are being brought into force in stages, so check
                  which parts are operative before relying on them.
                </p>
              </div>
            </Reveal>
          </div>
        )}

        {/* ── EVERYDAY ── */}
        {active === "everyday" && (
          <div className="space-y-8">
            <Reveal as="header">
              <h2 className="mb-3 font-serif text-3xl font-bold text-slate-900">
                What to do on an ordinary bad day
              </h2>
              <p className="max-w-3xl text-lg leading-relaxed text-gray-600">
                Four situations worth knowing before you are in them.
              </p>
            </Reveal>

            <div className="grid gap-4 md:grid-cols-2">
              {EVERYDAY.map((e, i) => (
                <Reveal key={e.title} delay={(i % 2) * 0.08}>
                  <div className="lift flex h-full flex-col rounded-2xl border border-gray-200 bg-white p-7 hover:border-amber-300 hover:shadow-md">
                    <span className="mb-5 flex h-11 w-11 items-center justify-center rounded-xl bg-amber-50 text-amber-700">
                      <e.icon className="h-5 w-5" aria-hidden="true" />
                    </span>
                    <h3 className="mb-3 font-serif text-xl font-semibold text-slate-900">
                      {e.title}
                    </h3>
                    <p className="mb-5 flex-1 text-[15px] leading-relaxed text-gray-600">
                      {e.body}
                    </p>
                    <p className="border-t border-gray-100 pt-4 font-mono text-xs text-gray-400">
                      {e.cite}
                    </p>
                  </div>
                </Reveal>
              ))}
            </div>

            <Reveal delay={0.1}>
              <div className="flex flex-col items-start gap-5 rounded-[2rem] border border-amber-200 bg-gradient-to-br from-amber-50 to-orange-50/50 p-8 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <h3 className="mb-2 font-serif text-2xl font-semibold text-amber-950">
                    Work out your own deadline
                  </h3>
                  <p className="max-w-lg text-[15px] leading-relaxed text-amber-900/80">
                    The toolkit turns any of these into dates, forums, forms and
                    costs for your situation — without an account.
                  </p>
                </div>
                <Link
                  href="/toolkit"
                  transitionTypes={["nav-forward"]}
                  className="lift inline-flex shrink-0 items-center gap-2 rounded-full bg-slate-900 px-7 py-3.5 font-medium text-white hover:bg-slate-800"
                >
                  Open the toolkit
                  <ArrowUpRight className="h-4 w-4" aria-hidden="true" />
                </Link>
              </div>
            </Reveal>
          </div>
        )}
      </main>
    </div>
  );
}
