"use client";

/**
 * One problem in, one plan out.
 *
 * The other tabs each answer a question nobody actually arrives with. A person
 * whose landlord kept their deposit does not want a limitation period; they
 * want to know what to do. Answering that needs the forum, the deadline, the
 * cost, the paperwork and the order — which the toolkit could already compute
 * but made the user assemble.
 *
 * So this asks for a situation and a date, and returns the whole thing. The
 * deadline leads, because it is the only part that expires, and an expired
 * claim makes the rest academic.
 */

import { useEffect, useState } from "react";
import {
  AlertTriangle,
  CalendarClock,
  CheckCircle2,
  ClipboardList,
  FileText,
  IndianRupee,
  Landmark,
  Loader2,
  Sparkles,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuthGate } from "@/lib/auth/AuthGate";
import {
  API,
  Label,
  SectionCard,
  buttonClass,
  formatDate,
  inputClass,
  postJSON,
  urgencyTone,
} from "./shared";

interface SituationMeta {
  id: string;
  label: string;
  summary: string;
  date_question: string;
  value_question: string | null;
  needs_value: boolean;
}

interface PlanDeadline {
  rule_id: string;
  label: string;
  trigger: string;
  citation: string;
  has_limitation: boolean;
  deadline: string | null;
  filing_date: string | null;
  days_remaining: number | null;
  expired: boolean;
  urgency: string;
  condonable: boolean;
  condonation_note: string;
  notes: string[];
}

interface CasePlan {
  situation_id: string;
  label: string;
  summary: string;
  event_date: string;
  headline: string;
  forum: {
    name: string;
    where: string;
    fee: string;
    how_to_file: string;
    documents: string[];
    lawyer_needed: string;
    typical_duration: string;
    notes: string[];
  };
  value_tier: string | null;
  deadlines: PlanDeadline[];
  steps: string[];
  documents_to_gather: string[];
  fee: { forum: string; amount: string; exact: boolean; basis: string } | null;
  template: { id: string; title: string; description: string } | null;
  stages: { label: string; date: string; note?: string }[];
  law: string[];
}

export function CasePlanTool({
  onError,
  onOpenTemplate,
  initialSituation = "",
  initialDate = "",
}: {
  onError: (m: string | null) => void;
  /** Hand the user to the drafting tab with the right template already chosen. */
  onOpenTemplate?: (templateId: string) => void;
  /** Pre-selected by the document analyser, which already knows both of these. */
  initialSituation?: string;
  initialDate?: string;
}) {
  const { requireAuth } = useAuthGate();
  const [situations, setSituations] = useState<SituationMeta[]>([]);
  const [situationId, setSituationId] = useState(initialSituation);
  const [eventDate, setEventDate] = useState(initialDate);
  const [value, setValue] = useState("");
  const [plan, setPlan] = useState<CasePlan | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    fetch(`${API}/api/tools/plan`)
      .then((r) => r.json())
      .then((d) => setSituations(d.situations ?? []))
      .catch(() => onError("Could not load the situation list."));
  }, [onError]);

  // The parent reads these out of the URL after mount, so the initial state
  // above misses them. Adopt them when they arrive, but never overwrite a
  // choice the user has already made themselves.
  useEffect(() => {
    if (initialSituation) setSituationId((current) => current || initialSituation);
  }, [initialSituation]);

  useEffect(() => {
    if (initialDate) setEventDate((current) => current || initialDate);
  }, [initialDate]);

  const situation = situations.find((s) => s.id === situationId) ?? null;

  const compute = async () => {
    setBusy(true);
    onError(null);
    try {
      setPlan(
        await postJSON<CasePlan>("/api/tools/plan", {
          situation_id: situationId,
          event_date: eventDate,
          claim_value: value ? Number(value) : null,
        }),
      );
    } catch (e) {
      onError(e instanceof Error ? e.message : "Something went wrong");
    } finally {
      setBusy(false);
    }
  };

  const run = () => requireAuth(compute, "Sign in to build your case plan.");

  const tone = plan?.deadlines[0]
    ? urgencyTone[plan.deadlines[0].urgency] ?? urgencyTone.none
    : urgencyTone.none;

  return (
    <div className="space-y-5">
      <SectionCard>
        <div className="space-y-4">
          <div>
            <Label>What has happened?</Label>
            <select
              value={situationId}
              onChange={(e) => {
                setSituationId(e.target.value);
                setPlan(null);
              }}
              className={inputClass}
            >
              <option value="">Choose your situation…</option>
              {situations.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.label}
                </option>
              ))}
            </select>
            {situation && (
              <p className="mt-2 text-sm text-gray-600">{situation.summary}</p>
            )}
          </div>

          {situation && (
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <Label>{situation.date_question}</Label>
                <input
                  type="date"
                  value={eventDate}
                  max={new Date().toISOString().slice(0, 10)}
                  onChange={(e) => {
                    setEventDate(e.target.value);
                    setPlan(null);
                  }}
                  className={inputClass}
                />
              </div>
              {situation.needs_value && (
                <div>
                  <Label>{situation.value_question}</Label>
                  <input
                    type="number"
                    inputMode="numeric"
                    min={0}
                    placeholder="₹"
                    value={value}
                    onChange={(e) => {
                      setValue(e.target.value);
                      setPlan(null);
                    }}
                    className={inputClass}
                  />
                </div>
              )}
            </div>
          )}

          <button
            type="button"
            onClick={run}
            disabled={!situationId || !eventDate || busy}
            className={buttonClass}
          >
            {busy ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Sparkles className="h-4 w-4" />
            )}
            {busy ? "Working…" : "Build my plan"}
          </button>
        </div>
      </SectionCard>

      {plan && (
        <>
          {/* The deadline leads. Nothing else matters if it has passed. */}
          <SectionCard className={cn("animate-fade-in-up border-2", tone.box)}>
            <div className="flex items-start gap-3">
              <CalendarClock className={cn("mt-0.5 h-5 w-5 shrink-0", tone.text)} />
              <div className="min-w-0">
                <p className={cn("font-serif text-lg font-bold", tone.text)}>
                  {plan.headline}
                </p>
                <p className="mt-1 text-sm text-gray-600">
                  Counted from {formatDate(plan.event_date)}.
                </p>
              </div>
            </div>
          </SectionCard>

          {plan.deadlines.length > 0 && (
            <SectionCard className="animate-fade-in-up">
              <h2 className="mb-4 font-serif text-xl font-bold text-slate-900">
                Your deadlines
              </h2>
              <ul className="space-y-3">
                {plan.deadlines.map((d) => {
                  const t = urgencyTone[d.urgency] ?? urgencyTone.none;
                  return (
                    <li
                      key={d.rule_id}
                      className={cn("rounded-xl border p-4", t.box)}
                    >
                      <div className="flex flex-wrap items-baseline justify-between gap-2">
                        <span className="font-medium text-slate-900">{d.label}</span>
                        <span className={cn("text-sm font-semibold", t.text)}>
                          {d.has_limitation
                            ? d.expired
                              ? "Expired"
                              : `${d.days_remaining} days left`
                            : "No time limit"}
                        </span>
                      </div>
                      {d.has_limitation && (
                        <p className="mt-1 text-sm text-gray-700">
                          File by <strong>{formatDate(d.filing_date ?? d.deadline)}</strong>
                        </p>
                      )}
                      <p className="mt-1 text-xs text-gray-500">
                        Runs from {d.trigger}. {d.citation}
                      </p>
                      {d.condonable && d.condonation_note && (
                        <p className="mt-2 text-xs text-gray-600">{d.condonation_note}</p>
                      )}
                    </li>
                  );
                })}
              </ul>
            </SectionCard>
          )}

          <SectionCard className="animate-fade-in-up">
            <h2 className="mb-1 flex items-center gap-2 font-serif text-xl font-bold text-slate-900">
              <ClipboardList className="h-5 w-5 text-gray-400" />
              What to do, in order
            </h2>
            <ol className="mt-4 space-y-3">
              {plan.steps.map((step, i) => (
                <li key={i} className="flex gap-3">
                  <span className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-slate-900 text-xs font-semibold text-white">
                    {i + 1}
                  </span>
                  <span className="text-sm text-gray-700">{step}</span>
                </li>
              ))}
            </ol>
          </SectionCard>

          <SectionCard className="animate-fade-in-up">
            <h2 className="mb-3 flex items-center gap-2 font-serif text-xl font-bold text-slate-900">
              <Landmark className="h-5 w-5 text-gray-400" />
              Where to file
            </h2>
            <p className="font-medium text-slate-900">{plan.forum.name}</p>
            <p className="mt-1 text-sm text-gray-600">{plan.forum.where}</p>
            {plan.value_tier && (
              <p className="mt-2 inline-block rounded-full bg-gray-100 px-3 py-1 text-xs font-medium text-gray-700">
                {plan.value_tier}
              </p>
            )}
            <dl className="mt-4 grid gap-3 text-sm sm:grid-cols-2">
              <div>
                <dt className="text-gray-500">How to file</dt>
                <dd className="text-gray-800">{plan.forum.how_to_file}</dd>
              </div>
              <div>
                <dt className="text-gray-500">Do you need a lawyer?</dt>
                <dd className="text-gray-800">{plan.forum.lawyer_needed}</dd>
              </div>
              {plan.forum.typical_duration && (
                <div>
                  <dt className="text-gray-500">How long it usually takes</dt>
                  <dd className="text-gray-800">{plan.forum.typical_duration}</dd>
                </div>
              )}
              {plan.fee && (
                <div>
                  <dt className="flex items-center gap-1 text-gray-500">
                    <IndianRupee className="h-3.5 w-3.5" />
                    What it costs
                  </dt>
                  <dd className="text-gray-800">
                    {plan.fee.amount}
                    {!plan.fee.exact && (
                      <span className="text-gray-500"> (estimate — confirm locally)</span>
                    )}
                  </dd>
                </div>
              )}
            </dl>
            {plan.forum.notes.length > 0 && (
              <ul className="mt-4 space-y-1.5">
                {plan.forum.notes.map((n, i) => (
                  <li key={i} className="flex gap-2 text-sm text-gray-600">
                    <AlertTriangle className="mt-0.5 h-3.5 w-3.5 shrink-0 text-amber-500" />
                    {n}
                  </li>
                ))}
              </ul>
            )}
          </SectionCard>

          {plan.documents_to_gather.length > 0 && (
            <SectionCard className="animate-fade-in-up">
              <h2 className="mb-3 font-serif text-xl font-bold text-slate-900">
                What to gather
              </h2>
              <ul className="space-y-2">
                {plan.documents_to_gather.map((d, i) => (
                  <li key={i} className="flex gap-2 text-sm text-gray-700">
                    <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-gray-300" />
                    {d}
                  </li>
                ))}
              </ul>
            </SectionCard>
          )}

          {plan.template && (
            <SectionCard className="animate-fade-in-up">
              <h2 className="mb-2 flex items-center gap-2 font-serif text-xl font-bold text-slate-900">
                <FileText className="h-5 w-5 text-gray-400" />
                The letter to send first
              </h2>
              <p className="font-medium text-slate-900">{plan.template.title}</p>
              <p className="mt-1 text-sm text-gray-600">{plan.template.description}</p>
              {onOpenTemplate && (
                <button
                  type="button"
                  onClick={() => onOpenTemplate(plan.template!.id)}
                  className="mt-4 rounded-full border border-gray-200 px-5 py-2 text-sm font-medium text-slate-900 transition-colors hover:border-gray-300 hover:bg-gray-50"
                >
                  Draft it now →
                </button>
              )}
            </SectionCard>
          )}

          {plan.stages.length > 0 && (
            <SectionCard className="animate-fade-in-up">
              <h2 className="mb-4 font-serif text-xl font-bold text-slate-900">
                What happens after you file
              </h2>
              <ol className="space-y-3 border-l border-gray-200 pl-5">
                {plan.stages.map((s, i) => (
                  <li key={i} className="relative">
                    <span className="absolute -left-[1.6rem] top-1.5 h-2 w-2 rounded-full bg-gray-300" />
                    <p className="text-sm font-medium text-slate-900">{s.label}</p>
                    <p className="text-xs text-gray-500">{formatDate(s.date)}</p>
                  </li>
                ))}
              </ol>
            </SectionCard>
          )}
        </>
      )}
    </div>
  );
}
