"use client";

/**
 * Citation extractor.
 *
 * Paste a judgment and get the authorities out of it: reported cases, statutes
 * and sections, separated into the ones the court relied on and the ones it
 * merely mentioned. Where a statute matches the corpus, the assistant can go
 * on to explain it.
 *
 * The extractor deliberately under-claims. A statute it cannot resolve to a
 * passage is listed as unresolved rather than linked to a near match, because
 * a citation pointing at the wrong provision is worse than no link at all —
 * the reader trusts it and stops checking.
 */

import { useState } from "react";
import {
  BookOpen,
  FileSearch,
  Gavel,
  Loader2,
  Quote,
  ScrollText,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuthGate } from "@/lib/auth/AuthGate";
import { Label, SectionCard, buttonClass, inputClass, postJSON } from "./shared";

interface Citation {
  text: string;
  kind: string;
  context: string;
  count: number;
  act: string | null;
  section: string | null;
  passage_id: string | null;
  passage_title: string | null;
  relied_on: boolean;
}

interface ExtractionResult {
  word_count: number;
  cases: Citation[];
  statutes: Citation[];
  unresolved: string[];
}

const SAMPLE = `In Kalyan Dey Chowdhury v. Rita Dey Chowdhury Nee Nandy, (2017) 14 SCC 200, this Court held that 25% of the husband's net salary would be just and proper as maintenance. Relying on Rajnesh v. Neha, (2021) 2 SCC 324, the Family Court directed both parties to file an Affidavit of Disclosure of Assets and Liabilities.

The appellant contended that Section 125 of the Code of Criminal Procedure, 1973 had no application. That contention is misconceived. As observed in Chaturbhuj v. Sita Bai, (2008) 2 SCC 316, the object of the provision is to prevent vagrancy and destitution.

Reference was also made to Section 24 of the Hindu Marriage Act, 1955 and to Order VII Rule 11 of the Code of Civil Procedure, 1908.`;

/** One authority, with its provenance shown rather than asserted. */
function CitationRow({ citation }: { citation: Citation }) {
  return (
    <li className="rounded-xl border border-gray-200 p-4">
      <div className="flex flex-wrap items-start justify-between gap-2">
        <p className="font-medium text-slate-900">{citation.text}</p>
        <div className="flex shrink-0 items-center gap-1.5">
          {citation.count > 1 && (
            <span className="rounded-full bg-gray-100 px-2 py-0.5 text-[11px] font-medium text-gray-600">
              {citation.count}×
            </span>
          )}
          {citation.relied_on ? (
            <span className="rounded-full bg-amber-50 px-2 py-0.5 text-[11px] font-medium text-amber-800">
              Relied on
            </span>
          ) : (
            <span className="rounded-full bg-gray-50 px-2 py-0.5 text-[11px] font-medium text-gray-500">
              Mentioned
            </span>
          )}
        </div>
      </div>

      {citation.passage_title && (
        <p className="mt-1.5 flex items-start gap-1.5 text-sm text-emerald-800">
          <BookOpen className="mt-0.5 h-3.5 w-3.5 shrink-0" />
          Explained in the knowledge base: {citation.passage_title}
        </p>
      )}

      {citation.context && (
        <p className="mt-2 flex gap-2 border-l-2 border-gray-200 pl-3 text-sm italic text-gray-600">
          <Quote className="mt-0.5 h-3 w-3 shrink-0 text-gray-300" />
          {citation.context}
        </p>
      )}
    </li>
  );
}

export function CitationsTool({ onError }: { onError: (m: string | null) => void }) {
  const { requireAuth } = useAuthGate();
  const [text, setText] = useState("");
  const [result, setResult] = useState<ExtractionResult | null>(null);
  const [busy, setBusy] = useState(false);

  const extract = async () => {
    setBusy(true);
    onError(null);
    try {
      setResult(await postJSON<ExtractionResult>("/api/tools/citations", { text }));
    } catch (e) {
      onError(e instanceof Error ? e.message : "Something went wrong");
    } finally {
      setBusy(false);
    }
  };

  const run = () =>
    requireAuth(extract, "Sign in to pull the authorities out of this judgment.");

  const reliedCount =
    (result?.cases.filter((c) => c.relied_on).length ?? 0) +
    (result?.statutes.filter((c) => c.relied_on).length ?? 0);

  return (
    <div className="space-y-5">
      <SectionCard>
        <div className="space-y-4">
          <div>
            <div className="flex flex-wrap items-baseline justify-between gap-2">
              <Label>Paste the judgment, order or brief</Label>
              <button
                onClick={() => {
                  setText(SAMPLE);
                  setResult(null);
                }}
                className="mb-1.5 text-xs font-medium text-gray-500 underline underline-offset-2 hover:text-gray-800"
              >
                Use a sample
              </button>
            </div>
            <textarea
              rows={10}
              value={text}
              onChange={(e) => {
                setText(e.target.value);
                setResult(null);
              }}
              placeholder="Paste the text here. Nothing is uploaded to a model — the extraction runs on patterns, locally on the server."
              className={cn(inputClass, "resize-y font-mono text-[13px] leading-relaxed")}
            />
            <p className="mt-1.5 text-xs text-gray-500">
              {text.trim().split(/\s+/).filter(Boolean).length.toLocaleString("en-IN")} words
              {text.length > 0 && text.length < 20 && " — needs at least 20 characters"}
            </p>
          </div>

          <button onClick={run} disabled={text.trim().length < 20 || busy} className={buttonClass}>
            {busy ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <FileSearch className="h-4 w-4" />
            )}
            Extract authorities
          </button>
        </div>
      </SectionCard>

      {result && (
        <>
          <SectionCard className="animate-fade-in-up">
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
              {[
                ["Words", result.word_count.toLocaleString("en-IN")],
                ["Cases", result.cases.length],
                ["Statutes", result.statutes.length],
                ["Relied on", reliedCount],
              ].map(([label, value]) => (
                <div key={label}>
                  <p className="text-xs font-semibold uppercase tracking-wider text-gray-400">
                    {label}
                  </p>
                  <p className="mt-0.5 font-serif text-2xl font-bold tabular-nums text-slate-900">
                    {value}
                  </p>
                </div>
              ))}
            </div>
            <p className="mt-4 border-t border-gray-100 pt-3 text-xs text-gray-500">
              &ldquo;Relied on&rdquo; is inferred from the language around the citation —
              treat it as a reading aid, not a holding.
            </p>
          </SectionCard>

          {result.cases.length > 0 && (
            <SectionCard className="animate-fade-in-up">
              <h2 className="mb-3 flex items-center gap-2 font-serif text-xl font-bold text-slate-900">
                <Gavel className="h-5 w-5 text-amber-600" />
                Cases
              </h2>
              <ul className="space-y-2.5">
                {result.cases.map((c, i) => (
                  <CitationRow key={`${c.text}-${i}`} citation={c} />
                ))}
              </ul>
            </SectionCard>
          )}

          {result.statutes.length > 0 && (
            <SectionCard className="animate-fade-in-up">
              <h2 className="mb-3 flex items-center gap-2 font-serif text-xl font-bold text-slate-900">
                <ScrollText className="h-5 w-5 text-slate-500" />
                Statutes
              </h2>
              <ul className="space-y-2.5">
                {result.statutes.map((c, i) => (
                  <CitationRow key={`${c.text}-${i}`} citation={c} />
                ))}
              </ul>
            </SectionCard>
          )}

          {result.unresolved.length > 0 && (
            <SectionCard className="animate-fade-in-up">
              <h3 className="text-sm font-semibold text-gray-900">
                Cited, but not in the knowledge base
              </h3>
              <p className="mt-1 text-sm text-gray-600">
                These were recognised as provisions but could not be matched to a
                passage with confidence, so they are listed rather than linked to a
                near miss.
              </p>
              <ul className="mt-3 flex flex-wrap gap-2">
                {result.unresolved.map((u, i) => (
                  <li
                    key={i}
                    className="rounded-full bg-gray-100 px-3 py-1 text-xs text-gray-700"
                  >
                    {u}
                  </li>
                ))}
              </ul>
            </SectionCard>
          )}

          {result.cases.length === 0 && result.statutes.length === 0 && (
            <SectionCard className="animate-fade-in-up">
              <p className="text-sm text-gray-600">
                No citations found. The extractor looks for reported citations
                (SCC, AIR, neutral), case names in the <em>A v. B</em> form, and
                sections named with their Act — so a passage of pure narrative will
                correctly yield nothing.
              </p>
            </SectionCard>
          )}
        </>
      )}
    </div>
  );
}
