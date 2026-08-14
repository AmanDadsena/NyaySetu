"use client";

/**
 * Court fee estimator.
 *
 * Fees are exact for centrally prescribed forums and an estimate for civil
 * suits, where each State sets its own ad valorem slabs. The distinction is
 * shown rather than hidden — an under-stamped plaint is returned for deficit,
 * so "approximately, confirm locally" is the useful answer, not a confident
 * number that may be wrong.
 */

import { useEffect, useMemo, useState } from "react";
import { AlertCircle, IndianRupee, Loader2 } from "lucide-react";
import { useAuthGate } from "@/lib/auth/AuthGate";
import {
  API,
  Label,
  SectionCard,
  buttonClass,
  inputClass,
  postJSON,
} from "./shared";

interface FeeMatter {
  id: string;
  label: string;
  needs_value: boolean;
  needs_state: boolean;
}

interface FeeResult {
  forum: string;
  amount: string;
  exact: boolean;
  basis: string;
  authority: string;
  notes: string[];
  additional: string[];
}

export function FeesTool({ onError }: { onError: (m: string | null) => void }) {
  const { requireAuth } = useAuthGate();
  const [matters, setMatters] = useState<FeeMatter[]>([]);
  const [states, setStates] = useState<{ id: string; label: string }[]>([]);
  const [matterId, setMatterId] = useState("");
  const [value, setValue] = useState("");
  const [state, setState] = useState("");
  const [result, setResult] = useState<FeeResult | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    fetch(`${API}/api/tools/fees`)
      .then((r) => r.json())
      .then((d) => {
        setMatters(d.matters ?? []);
        setStates(d.states ?? []);
      })
      .catch(() => onError("Could not load fee data."));
  }, [onError]);

  const matter = useMemo(
    () => matters.find((m) => m.id === matterId) ?? null,
    [matters, matterId],
  );

  const compute = async () => {
    setBusy(true);
    onError(null);
    try {
      setResult(
        await postJSON<FeeResult>("/api/tools/fees", {
          matter: matterId,
          value: value ? Number(value) : 0,
          state: state || null,
        }),
      );
    } catch (e) {
      onError(e instanceof Error ? e.message : "Something went wrong");
    } finally {
      setBusy(false);
    }
  };

  const run = () => requireAuth(compute, "Sign in to estimate what filing will cost.");

  return (
    <div className="space-y-5">
      <SectionCard>
        <div className="space-y-4">
          <div>
            <Label>What are you filing?</Label>
            <select
              value={matterId}
              onChange={(e) => {
                setMatterId(e.target.value);
                setResult(null);
              }}
              className={inputClass}
            >
              <option value="">Select…</option>
              {matters.map((m) => (
                <option key={m.id} value={m.id}>
                  {m.label}
                </option>
              ))}
            </select>
          </div>

          {matter?.needs_value && (
            <div>
              <Label>Value of the claim (₹)</Label>
              <input
                type="number"
                inputMode="numeric"
                value={value}
                onChange={(e) => setValue(e.target.value)}
                placeholder="e.g. 250000"
                className={inputClass}
              />
            </div>
          )}

          {matter?.needs_state && (
            <div>
              <Label>State</Label>
              <select
                value={state}
                onChange={(e) => setState(e.target.value)}
                className={inputClass}
              >
                <option value="">Select a State…</option>
                {states.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.label}
                  </option>
                ))}
              </select>
            </div>
          )}

          <button onClick={run} disabled={!matterId || busy} className={buttonClass}>
            {busy ? <Loader2 className="h-4 w-4 animate-spin" /> : <IndianRupee className="h-4 w-4" />}
            Estimate fee
          </button>
        </div>
      </SectionCard>

      {result && (
        <SectionCard className="animate-fade-in-up">
          <p className="text-xs font-semibold uppercase tracking-wider text-gray-400">
            {result.forum}
          </p>
          <p className="mt-1.5 font-serif text-3xl font-bold text-slate-900">{result.amount}</p>
          <p className="mt-1 text-sm text-gray-600">{result.basis}</p>

          {!result.exact && (
            <div className="mt-4 flex items-start gap-2 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3">
              <AlertCircle className="mt-0.5 h-4 w-4 shrink-0 text-amber-600" />
              <p className="text-sm text-amber-900">
                This is an estimate. Confirm at the filing counter of the court you are
                filing in — they will tell you exactly, and it costs nothing to ask.
              </p>
            </div>
          )}

          {result.notes.length > 0 && (
            <ul className="mt-4 space-y-2">
              {result.notes.map((n, i) => (
                <li key={i} className="flex gap-2 text-sm text-gray-600">
                  <span className="mt-2 h-1 w-1 shrink-0 rounded-full bg-gray-400" />
                  {n}
                </li>
              ))}
            </ul>
          )}

          {result.additional.length > 0 && (
            <div className="mt-5 border-t border-gray-100 pt-4">
              <h3 className="mb-2 text-sm font-semibold text-gray-900">
                Also budget for
              </h3>
              <ul className="space-y-1.5">
                {result.additional.map((a, i) => (
                  <li key={i} className="text-sm text-gray-600">
                    {a}
                  </li>
                ))}
              </ul>
            </div>
          )}

          <p className="mt-4 border-t border-gray-100 pt-3 text-xs text-gray-500">
            {result.authority}
          </p>
        </SectionCard>
      )}
    </div>
  );
}
