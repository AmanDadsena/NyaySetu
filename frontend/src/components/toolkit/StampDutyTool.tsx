"use client";

/**
 * Stamp duty and registration estimator.
 *
 * The number is the least useful thing on this screen. Two things above it
 * matter more, and both are shown before the total:
 *
 *   * duty runs on the higher of the price and the circle rate, so entering a
 *     lower price does not lower the bill; and
 *   * several States charge women buyers less, and the concession is not
 *     applied by anyone unless it is claimed.
 *
 * Where a State gives no concession, that is stated too, so a buyer who
 * expected one learns there is none rather than wondering whether the tool
 * forgot to apply it.
 */

import { useEffect, useMemo, useState } from "react";
import { AlertCircle, BadgeIndianRupee, Landmark, Loader2, TrendingDown } from "lucide-react";
import { useAuthGate } from "@/lib/auth/AuthGate";
import { API, Label, SectionCard, buttonClass, inputClass, postJSON } from "./shared";

interface Instrument {
  id: string;
  label: string;
  needs_value: boolean;
  needs_state: boolean;
  needs_buyer: boolean;
  value_label: string;
}

interface StampDutyResult {
  instrument: string;
  duty: string;
  registration_fee: string;
  total: string;
  exact: boolean;
  charged_on: string;
  basis: string;
  authority: string;
  concession: string;
  concession_forgone: string;
  notes: string[];
  additional: string[];
}

export function StampDutyTool({ onError }: { onError: (m: string | null) => void }) {
  const { requireAuth } = useAuthGate();
  const [instruments, setInstruments] = useState<Instrument[]>([]);
  const [states, setStates] = useState<{ id: string; label: string }[]>([]);
  const [buyers, setBuyers] = useState<{ id: string; label: string }[]>([]);

  const [instrumentId, setInstrumentId] = useState("");
  const [value, setValue] = useState("");
  const [circleRate, setCircleRate] = useState("");
  const [state, setState] = useState("");
  const [buyer, setBuyer] = useState("man");
  const [result, setResult] = useState<StampDutyResult | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    fetch(`${API}/api/tools/stamp-duty`)
      .then((r) => r.json())
      .then((d) => {
        setInstruments(d.instruments ?? []);
        setStates(d.states ?? []);
        setBuyers(d.buyers ?? []);
      })
      .catch(() => onError("Could not load stamp duty data."));
  }, [onError]);

  const instrument = useMemo(
    () => instruments.find((i) => i.id === instrumentId) ?? null,
    [instruments, instrumentId],
  );

  const compute = async () => {
    setBusy(true);
    onError(null);
    try {
      setResult(
        await postJSON<StampDutyResult>("/api/tools/stamp-duty", {
          instrument: instrumentId,
          value: value ? Number(value) : 0,
          circle_rate: circleRate ? Number(circleRate) : 0,
          state: state || null,
          buyer,
        }),
      );
    } catch (e) {
      onError(e instanceof Error ? e.message : "Something went wrong");
    } finally {
      setBusy(false);
    }
  };

  const run = () =>
    requireAuth(compute, "Sign in to estimate the duty on your instrument.");

  const ready = !!instrumentId && (!instrument?.needs_state || !!state);

  return (
    <div className="space-y-5">
      <SectionCard>
        <div className="space-y-4">
          <div>
            <Label>What are you having stamped?</Label>
            <select
              value={instrumentId}
              onChange={(e) => {
                setInstrumentId(e.target.value);
                setResult(null);
              }}
              className={inputClass}
            >
              <option value="">Select an instrument…</option>
              {instruments.map((i) => (
                <option key={i.id} value={i.id}>
                  {i.label}
                </option>
              ))}
            </select>
          </div>

          {instrument?.needs_value && (
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <Label>{instrument.value_label}</Label>
                <input
                  type="number"
                  inputMode="numeric"
                  value={value}
                  onChange={(e) => setValue(e.target.value)}
                  placeholder="e.g. 5000000"
                  className={inputClass}
                />
              </div>
              {instrument.id !== "lease" && (
                <div>
                  <Label>
                    Circle rate value
                    <span className="ml-1 font-normal text-gray-400">(optional)</span>
                  </Label>
                  <input
                    type="number"
                    inputMode="numeric"
                    value={circleRate}
                    onChange={(e) => setCircleRate(e.target.value)}
                    placeholder="e.g. 6000000"
                    className={inputClass}
                  />
                  <p className="mt-1 text-xs text-gray-500">
                    Also called the ready reckoner or guidance value. Duty is charged
                    on whichever is higher.
                  </p>
                </div>
              )}
            </div>
          )}

          {instrument?.needs_state && (
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

          {instrument?.needs_buyer && (
            <div>
              <Label>Whose name will the property be in?</Label>
              <select
                value={buyer}
                onChange={(e) => setBuyer(e.target.value)}
                className={inputClass}
              >
                {buyers.map((b) => (
                  <option key={b.id} value={b.id}>
                    {b.label}
                  </option>
                ))}
              </select>
              <p className="mt-1 text-xs text-gray-500">
                Several States charge women buyers a lower rate. It has to be claimed.
              </p>
            </div>
          )}

          <button onClick={run} disabled={!ready || busy} className={buttonClass}>
            {busy ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <BadgeIndianRupee className="h-4 w-4" />
            )}
            Estimate duty
          </button>
        </div>
      </SectionCard>

      {result && (
        <SectionCard className="animate-fade-in-up">
          <p className="text-xs font-semibold uppercase tracking-wider text-gray-400">
            {result.instrument}
          </p>
          <p className="mt-1.5 font-serif text-3xl font-bold text-slate-900">
            {result.total}
          </p>
          <p className="mt-1 text-sm text-gray-600">{result.basis}</p>

          <dl className="mt-4 grid gap-4 border-t border-gray-100 pt-4 sm:grid-cols-3">
            {[
              ["Stamp duty", result.duty],
              ["Registration fee", result.registration_fee],
              ["Charged on", result.charged_on],
            ].map(([term, v]) => (
              <div key={term}>
                <dt className="text-xs font-semibold uppercase tracking-wider text-gray-400">
                  {term}
                </dt>
                <dd className="mt-1 text-sm font-medium text-gray-800">{v}</dd>
              </div>
            ))}
          </dl>

          {result.concession && (
            <div className="mt-4 flex items-start gap-2 rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3">
              <TrendingDown className="mt-0.5 h-4 w-4 shrink-0 text-emerald-600" />
              <p className="text-sm text-emerald-900">{result.concession}</p>
            </div>
          )}

          {result.concession_forgone && (
            <div className="mt-4 flex items-start gap-2 rounded-xl border border-sky-200 bg-sky-50 px-4 py-3">
              <Landmark className="mt-0.5 h-4 w-4 shrink-0 text-sky-600" />
              <p className="text-sm text-sky-900">
                Registering this in a woman&rsquo;s name instead would save{" "}
                <strong>{result.concession_forgone}</strong> in duty. Worth knowing
                before the deed is drawn — it cannot be changed afterwards without
                paying duty a second time.
              </p>
            </div>
          )}

          {!result.exact && (
            <div className="mt-4 flex items-start gap-2 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3">
              <AlertCircle className="mt-0.5 h-4 w-4 shrink-0 text-amber-600" />
              <p className="text-sm text-amber-900">
                An estimate. Rates change with every State budget and vary within a
                State by locality and property type. Confirm at the sub-registrar&rsquo;s
                office for the area the property falls in — they will tell you exactly,
                and it costs nothing to ask.
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
              <h3 className="mb-2 text-sm font-semibold text-gray-900">Also budget for</h3>
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
