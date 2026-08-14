"use client";

/**
 * Maintenance estimator.
 *
 * Every other tool in the toolkit answers a question. This one refuses to,
 * and the interface has to carry that refusal — because a person who walks
 * into a Family Court quoting a figure this app gave them has been misled by
 * it.
 *
 * So: the headline is a range with a dash in the middle, never a figure. The
 * precedent each band comes from sits beside the band. And the factors that
 * move an award are given equal visual weight to the arithmetic, because in
 * practice they decide more than the percentages do.
 */

import { useEffect, useState } from "react";
import {
  ArrowDownRight,
  ArrowUpRight,
  BookMarked,
  Loader2,
  Scale,
  ScrollText,
} from "lucide-react";
import { useAuthGate } from "@/lib/auth/AuthGate";
import { API, Label, SectionCard, buttonClass, inputClass, postJSON } from "./shared";

interface Precedent {
  case: string;
  citation: string;
  proposition: string;
}

interface Provision {
  id: string;
  label: string;
  was: string;
  who: string;
  where: string;
  why: string;
}

interface MaintenanceResult {
  monthly_low: string;
  monthly_high: string;
  share_low: string;
  share_high: string;
  covers: string;
  basis: string;
  exact: boolean;
  capped: boolean;
  breakdown: { for: string; share: string; amount: string; anchor: string }[];
  raises: string[];
  lowers: string[];
  precedents: Precedent[];
  provisions: Provision[];
  procedure: string[];
  notes: string[];
}

interface Reference {
  factors: string[];
  factors_source: string;
}

export function MaintenanceTool({ onError }: { onError: (m: string | null) => void }) {
  const { requireAuth } = useAuthGate();
  const [reference, setReference] = useState<Reference | null>(null);
  const [payerIncome, setPayerIncome] = useState("");
  const [claimantIncome, setClaimantIncome] = useState("");
  const [spouse, setSpouse] = useState(true);
  const [children, setChildren] = useState("0");
  const [parents, setParents] = useState("0");
  const [result, setResult] = useState<MaintenanceResult | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    fetch(`${API}/api/tools/maintenance`)
      .then((r) => r.json())
      .then(setReference)
      .catch(() => onError("Could not load maintenance reference data."));
  }, [onError]);

  const compute = async () => {
    setBusy(true);
    onError(null);
    try {
      setResult(
        await postJSON<MaintenanceResult>("/api/tools/maintenance", {
          payer_income: Number(payerIncome) || 0,
          claimant_income: Number(claimantIncome) || 0,
          spouse,
          children: Number(children) || 0,
          parents: Number(parents) || 0,
        }),
      );
    } catch (e) {
      onError(e instanceof Error ? e.message : "Something went wrong");
    } finally {
      setBusy(false);
    }
  };

  const run = () =>
    requireAuth(compute, "Sign in to see the range and the cases behind it.");

  const anyDependant = spouse || Number(children) > 0 || Number(parents) > 0;

  return (
    <div className="space-y-5">
      {/* The disclaimer leads. It is the most important thing here. */}
      <div className="rounded-2xl border border-amber-200 bg-amber-50 p-5">
        <h2 className="flex items-center gap-2 font-semibold text-amber-900">
          <Scale className="h-4 w-4 shrink-0" />
          There is no formula for maintenance
        </h2>
        <p className="mt-1.5 text-sm text-amber-900/90">
          No provision prescribes a percentage. The amount is discretionary, decided
          on the criteria in <em>Rajnesh v. Neha</em>. What follows is a range drawn
          from percentages actually awarded in reported cases — a starting point for
          a conversation with a lawyer, not an entitlement.
        </p>
      </div>

      <SectionCard>
        <div className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <Label>Respondent&rsquo;s net monthly income (₹)</Label>
              <input
                type="number"
                inputMode="numeric"
                value={payerIncome}
                onChange={(e) => {
                  setPayerIncome(e.target.value);
                  setResult(null);
                }}
                placeholder="e.g. 60000"
                className={inputClass}
              />
              <p className="mt-1 text-xs text-gray-500">
                Take-home after statutory deductions — courts work from net, not gross.
              </p>
            </div>
            <div>
              <Label>
                Claimant&rsquo;s own monthly income (₹)
                <span className="ml-1 font-normal text-gray-400">(if any)</span>
              </Label>
              <input
                type="number"
                inputMode="numeric"
                value={claimantIncome}
                onChange={(e) => {
                  setClaimantIncome(e.target.value);
                  setResult(null);
                }}
                placeholder="0"
                className={inputClass}
              />
              <p className="mt-1 text-xs text-gray-500">
                Earning something reduces the claim. It does not end it.
              </p>
            </div>
          </div>

          <div>
            <Label>Who is the maintenance claimed for?</Label>
            <div className="grid gap-3 sm:grid-cols-3">
              <label className="flex items-center gap-2 rounded-xl border border-gray-200 px-3.5 py-2.5 text-sm">
                <input
                  type="checkbox"
                  checked={spouse}
                  onChange={(e) => {
                    setSpouse(e.target.checked);
                    setResult(null);
                  }}
                  className="h-4 w-4 rounded border-gray-300 accent-black"
                />
                Spouse
              </label>
              <div>
                <select
                  value={children}
                  onChange={(e) => {
                    setChildren(e.target.value);
                    setResult(null);
                  }}
                  className={inputClass}
                >
                  {[0, 1, 2, 3, 4, 5].map((n) => (
                    <option key={n} value={n}>
                      {n === 0 ? "No children" : `${n} child${n > 1 ? "ren" : ""}`}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <select
                  value={parents}
                  onChange={(e) => {
                    setParents(e.target.value);
                    setResult(null);
                  }}
                  className={inputClass}
                >
                  {[0, 1, 2].map((n) => (
                    <option key={n} value={n}>
                      {n === 0 ? "No parents" : `${n} parent${n > 1 ? "s" : ""}`}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          <button
            onClick={run}
            disabled={!payerIncome || !anyDependant || busy}
            className={buttonClass}
          >
            {busy ? <Loader2 className="h-4 w-4 animate-spin" /> : <Scale className="h-4 w-4" />}
            Show the range
          </button>
        </div>
      </SectionCard>

      {result && (
        <>
          <SectionCard className="animate-fade-in-up">
            <p className="text-xs font-semibold uppercase tracking-wider text-gray-400">
              Reported awards in comparable cases · {result.covers}
            </p>
            <p className="mt-1.5 font-serif text-3xl font-bold tabular-nums text-slate-900 sm:text-4xl">
              {result.monthly_low}
              <span className="mx-2 font-sans text-2xl font-normal text-gray-300">–</span>
              {result.monthly_high}
            </p>
            <p className="mt-1 text-sm text-gray-600">
              a month, being {result.share_low} to {result.share_high}{" "}
              of the respondent&rsquo;s net income
            </p>

            {result.breakdown.length > 0 && (
              <div className="mt-5 space-y-2.5 border-t border-gray-100 pt-4">
                {result.capped && (
                  <p className="text-xs text-gray-500">
                    The lines below are the untrimmed bands. Together they exceed the
                    ceiling courts work to, so the headline range above is lower than
                    they sum to.
                  </p>
                )}
                {result.breakdown.map((b, i) => (
                  <div key={i} className="rounded-xl bg-gray-50 px-4 py-3">
                    <div className="flex flex-wrap items-baseline justify-between gap-x-3">
                      <p className="text-sm font-medium text-slate-900">{b.for}</p>
                      <p className="text-sm tabular-nums text-gray-700">{b.amount}</p>
                    </div>
                    <p className="mt-0.5 text-xs text-gray-500">{b.share}</p>
                    <p className="mt-1 text-xs italic text-gray-500">{b.anchor}</p>
                  </div>
                ))}
              </div>
            )}

            {result.notes.map((n, i) => (
              <p key={i} className="mt-3 text-sm text-gray-600">
                {n}
              </p>
            ))}
          </SectionCard>

          <div className="grid gap-5 sm:grid-cols-2">
            <SectionCard className="animate-fade-in-up">
              <h3 className="mb-3 flex items-center gap-2 text-sm font-semibold text-emerald-800">
                <ArrowUpRight className="h-4 w-4" />
                Pushes the figure up
              </h3>
              <ul className="space-y-2.5">
                {result.raises.map((r, i) => (
                  <li key={i} className="flex gap-2 text-sm text-gray-600">
                    <span className="mt-2 h-1 w-1 shrink-0 rounded-full bg-emerald-400" />
                    {r}
                  </li>
                ))}
              </ul>
            </SectionCard>

            <SectionCard className="animate-fade-in-up">
              <h3 className="mb-3 flex items-center gap-2 text-sm font-semibold text-gray-700">
                <ArrowDownRight className="h-4 w-4" />
                Pulls it down
              </h3>
              <ul className="space-y-2.5">
                {result.lowers.map((l, i) => (
                  <li key={i} className="flex gap-2 text-sm text-gray-600">
                    <span className="mt-2 h-1 w-1 shrink-0 rounded-full bg-gray-400" />
                    {l}
                  </li>
                ))}
              </ul>
            </SectionCard>
          </div>

          <SectionCard className="animate-fade-in-up">
            <h3 className="mb-3 flex items-center gap-2 font-serif text-xl font-bold text-slate-900">
              <BookMarked className="h-5 w-5 text-amber-600" />
              Where the numbers come from
            </h3>
            <ul className="space-y-3">
              {result.precedents.map((p, i) => (
                <li key={i} className="rounded-xl border border-gray-200 p-4">
                  <p className="font-medium text-slate-900">{p.case}</p>
                  <p className="mt-0.5 text-xs font-medium text-gray-500">{p.citation}</p>
                  <p className="mt-1.5 text-sm text-gray-600">{p.proposition}</p>
                </li>
              ))}
            </ul>
          </SectionCard>

          <SectionCard className="animate-fade-in-up">
            <h3 className="mb-3 flex items-center gap-2 font-serif text-xl font-bold text-slate-900">
              <ScrollText className="h-5 w-5 text-slate-500" />
              What to file, and where
            </h3>
            <div className="space-y-3">
              {result.provisions.map((p) => (
                <div key={p.id} className="rounded-xl border border-gray-200 p-4">
                  <p className="font-medium text-slate-900">{p.label}</p>
                  {p.was && (
                    <p className="mt-0.5 text-xs text-gray-500">Formerly {p.was}</p>
                  )}
                  <dl className="mt-2 space-y-1 text-sm">
                    <div className="flex gap-2">
                      <dt className="shrink-0 font-medium text-gray-500">Who:</dt>
                      <dd className="text-gray-700">{p.who}</dd>
                    </div>
                    <div className="flex gap-2">
                      <dt className="shrink-0 font-medium text-gray-500">Where:</dt>
                      <dd className="text-gray-700">{p.where}</dd>
                    </div>
                    <div className="flex gap-2">
                      <dt className="shrink-0 font-medium text-gray-500">Why:</dt>
                      <dd className="text-gray-700">{p.why}</dd>
                    </div>
                  </dl>
                </div>
              ))}
            </div>
          </SectionCard>

          <SectionCard className="animate-fade-in-up">
            <h3 className="mb-3 font-serif text-xl font-bold text-slate-900">
              Do these, in this order
            </h3>
            <ol className="space-y-2.5">
              {result.procedure.map((step, i) => (
                <li key={i} className="flex gap-2.5 text-sm text-gray-600">
                  <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-gray-100 text-[11px] font-semibold text-gray-600">
                    {i + 1}
                  </span>
                  {step}
                </li>
              ))}
            </ol>
          </SectionCard>
        </>
      )}

      {!result && reference && (
        <SectionCard>
          <h3 className="mb-2 text-sm font-semibold text-gray-900">
            What the court actually weighs
          </h3>
          <ul className="space-y-2">
            {reference.factors.map((f, i) => (
              <li key={i} className="flex gap-2 text-sm text-gray-600">
                <span className="mt-2 h-1 w-1 shrink-0 rounded-full bg-gray-400" />
                {f}
              </li>
            ))}
          </ul>
          <p className="mt-3 border-t border-gray-100 pt-3 text-xs text-gray-500">
            {reference.factors_source}
          </p>
        </SectionCard>
      )}
    </div>
  );
}
