/**
 * Shared chrome for the policy pages (privacy, terms, disclaimer, contact).
 *
 * These four pages exist because the footer links to them, and a footer that
 * links to a 404 is worse than a footer with no legal section at all. They are
 * written to describe what this application actually does — the tables it
 * writes to, the flags that gate logging, the things it cannot promise —
 * rather than to recite boilerplate borrowed from a SaaS template.
 *
 * The typography plugin is not installed in this project, so the prose helpers
 * below carry their own styles rather than relying on `prose` classes.
 */

import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import type { ReactNode } from "react";

export function LegalShell({
  title,
  lede,
  updated,
  children,
}: {
  title: string;
  lede: string;
  /** Human-readable date this text was last reviewed. */
  updated: string;
  children: ReactNode;
}) {
  return (
    <div className="bg-white">
      <header className="relative overflow-hidden border-b border-gray-100 bg-gradient-to-b from-amber-50/60 to-white">
        <div
          aria-hidden="true"
          className="animate-aurora pointer-events-none absolute -top-32 right-0 h-72 w-72 rounded-full bg-amber-300/20 blur-3xl"
        />
        <div className="relative mx-auto max-w-3xl px-6 pt-20 pb-14">
          <Link
            href="/"
            // Tagged `nav-back` so the page slides right on the way out —
            // the direction the reader expects when returning.
            className="mb-8 inline-flex items-center gap-2 text-sm font-medium text-gray-500 transition-colors hover:text-slate-900"
          >
            <ArrowLeft className="h-4 w-4" aria-hidden="true" />
            Back to Nyaysetu
          </Link>
          <h1 className="mb-4 font-serif text-4xl font-bold tracking-tight text-slate-900 md:text-5xl">
            {title}
          </h1>
          <p className="mb-6 text-lg leading-relaxed text-gray-600">{lede}</p>
          <p className="text-sm text-gray-400">Last reviewed {updated}</p>
        </div>
      </header>

      <main className="mx-auto max-w-3xl px-6 py-16">
        <div className="space-y-12">{children}</div>
      </main>
    </div>
  );
}

export function Section({
  heading,
  children,
}: {
  heading: string;
  children: ReactNode;
}) {
  return (
    <section className="scroll-mt-24">
      <h2 className="mb-4 font-serif text-2xl font-semibold text-slate-900">
        {heading}
      </h2>
      <div className="space-y-4 text-[15px] leading-relaxed text-gray-700">
        {children}
      </div>
    </section>
  );
}

/** A point that needs to stand out from the surrounding prose. */
export function Note({
  tone = "neutral",
  children,
}: {
  tone?: "neutral" | "warn";
  children: ReactNode;
}) {
  return (
    <div
      className={
        tone === "warn"
          ? "rounded-2xl border border-amber-200 bg-amber-50/70 p-5 text-[15px] leading-relaxed text-amber-950"
          : "rounded-2xl border border-gray-200 bg-gray-50 p-5 text-[15px] leading-relaxed text-gray-700"
      }
    >
      {children}
    </div>
  );
}

export function Bullets({ items }: { items: ReactNode[] }) {
  return (
    <ul className="space-y-2.5">
      {items.map((item, i) => (
        <li key={i} className="flex gap-3">
          <span
            aria-hidden="true"
            className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-400"
          />
          <span>{item}</span>
        </li>
      ))}
    </ul>
  );
}
