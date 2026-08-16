"use client";

/**
 * Site footer.
 *
 * The ordering here is a deliberate inversion of the usual. On most sites the
 * footer's most prominent block is a newsletter signup or a social row; here it
 * is the NALSA helpline, because free legal aid is a statutory entitlement
 * under the Legal Services Authorities Act, 1987 and a large share of the
 * people this app is built for qualify without knowing it. Someone who reads
 * nothing else on the page should still leave with that number.
 *
 * Everything below it — the disclaimer, the link to the source, the note that
 * answers cite their provision — exists so a reader can check the tool rather
 * than take its word.
 */

import Link from "next/link";
// lucide v1 dropped its brand icons, so `Code2` stands in for the GitHub mark.
import { Code2, ExternalLink, Phone, Scale } from "lucide-react";
import { useT } from "@/lib/i18n/LanguageProvider";
import { LEGAL_AID_HELPLINE } from "@/lib/site-stats";
import type { TranslationKey } from "@/lib/i18n/translations";

const API_DOCS = "https://amandadsena07-nyaysetu-backend.hf.space/docs";
const REPO = "https://github.com/AmanDadsena/Nyaysetu";

interface FooterLink {
  href: string;
  key: TranslationKey;
  external?: boolean;
}

const COLUMNS: { heading: TranslationKey; links: FooterLink[] }[] = [
  {
    heading: "footer.product",
    links: [
      { href: "/analyze", key: "nav.analyze" },
      { href: "/toolkit", key: "nav.toolkit" },
      { href: "/lawyers", key: "nav.lawyers" },
      { href: "/cases", key: "nav.cases" },
    ],
  },
  {
    heading: "footer.learn",
    links: [
      { href: "/how-it-works", key: "footer.howItWorks" },
      { href: "/knowledge", key: "nav.knowledge" },
      { href: "/about", key: "nav.about" },
    ],
  },
  {
    heading: "footer.legalCol",
    links: [
      { href: "/privacy", key: "footer.privacy" },
      { href: "/terms", key: "footer.terms" },
      { href: "/disclaimer", key: "footer.disclaimer" },
      { href: "/contact", key: "footer.contact" },
    ],
  },
  {
    heading: "footer.reference",
    links: [
      {
        href: "https://legislative.gov.in/constitution-of-india",
        key: "footer.constitution",
        external: true,
      },
      { href: "https://www.indiacode.nic.in", key: "footer.indiaCode", external: true },
      { href: "https://nalsa.gov.in", key: "footer.nalsa", external: true },
      { href: API_DOCS, key: "footer.apiDocs", external: true },
    ],
  },
];

export function Footer() {
  const t = useT();

  return (
    <footer className="relative mt-24 overflow-hidden bg-slate-950 text-slate-300">
      {/* A single soft wash of colour so the footer reads as a place rather
          than as the page running out. Pointer-events off — it is decoration
          and must never sit between a reader and a link. */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute -top-40 left-1/2 h-80 w-[46rem] -translate-x-1/2 rounded-full bg-amber-500/10 blur-3xl"
      />

      <div className="relative mx-auto max-w-7xl px-6 pt-16 pb-10">
        {/* ── Free legal aid ─── */}
        <div className="mb-16 grid gap-8 rounded-3xl border border-amber-500/20 bg-gradient-to-br from-amber-500/10 to-transparent p-8 md:grid-cols-[1fr_auto] md:items-center md:p-10">
          <div>
            <h2 className="mb-3 font-serif text-2xl font-semibold text-amber-300 md:text-3xl">
              {t("footer.aidTitle")}
            </h2>
            <p className="max-w-2xl text-sm leading-relaxed text-slate-300/90">
              {t("footer.aidBody")}
            </p>
          </div>
          <a
            href={`tel:${LEGAL_AID_HELPLINE}`}
            className="lift inline-flex shrink-0 items-center justify-center gap-3 rounded-full bg-amber-400 px-7 py-4 text-base font-semibold text-slate-950 shadow-lg shadow-amber-500/20 hover:bg-amber-300 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-amber-300"
          >
            <Phone className="h-5 w-5" aria-hidden="true" />
            {t("footer.aidCall")}
          </a>
        </div>

        {/* ── Identity + link columns ─── */}
        <div className="grid gap-12 lg:grid-cols-[1.4fr_3fr]">
          <div>
            <Link href="/" className="group mb-5 inline-flex items-center gap-3">
              <span className="flex h-10 w-10 items-center justify-center overflow-hidden rounded-xl border border-white/10 bg-white/5">
                <Scale className="h-5 w-5 text-amber-400" aria-hidden="true" />
              </span>
              <span className="flex items-center font-serif text-xl tracking-tight">
                <span className="font-bold text-white">Nyay</span>
                <span className="font-medium text-amber-400">setu</span>
              </span>
            </Link>
            <p className="mb-6 max-w-sm text-sm leading-relaxed text-slate-400">
              {t("footer.tagline")}
            </p>
            <div className="flex flex-wrap gap-2">
              {(["footer.openSource", "footer.noAccount", "footer.builtFor"] as const).map(
                (key) => (
                  <span
                    key={key}
                    className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs font-medium text-slate-400"
                  >
                    {t(key)}
                  </span>
                ),
              )}
            </div>
          </div>

          <nav
            aria-label="Footer"
            className="grid grid-cols-2 gap-x-6 gap-y-10 sm:grid-cols-4"
          >
            {COLUMNS.map((column) => (
              <div key={column.heading}>
                <h3 className="mb-4 text-xs font-semibold tracking-[0.12em] text-slate-500 uppercase">
                  {t(column.heading)}
                </h3>
                <ul className="space-y-3">
                  {column.links.map((link) => (
                    <li key={link.href}>
                      {link.external ? (
                        <a
                          href={link.href}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-1.5 text-sm text-slate-400 transition-colors hover:text-white"
                        >
                          {t(link.key)}
                          <ExternalLink className="h-3 w-3 shrink-0 opacity-60" aria-hidden="true" />
                        </a>
                      ) : (
                        <Link
                          href={link.href}
                          className="text-sm text-slate-400 transition-colors hover:text-white"
                        >
                          {t(link.key)}
                        </Link>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </nav>
        </div>

        {/* ── Disclaimer ───
            Last thing on the page, and unmissable. This is the sentence that
            keeps the whole site honest about what it is. */}
        <div className="mt-16 border-t border-white/10 pt-8">
          <p className="mb-6 max-w-4xl text-sm leading-relaxed text-slate-400">
            {t("footer.notAdvice")}
          </p>
          <div className="flex flex-col items-start justify-between gap-4 text-xs text-slate-500 sm:flex-row sm:items-center">
            <p>
              © {new Date().getFullYear()} Nyaysetu · MIT licensed
            </p>
            <a
              href={REPO}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 transition-colors hover:text-slate-300"
            >
              <Code2 className="h-4 w-4" aria-hidden="true" />
              Source code
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
