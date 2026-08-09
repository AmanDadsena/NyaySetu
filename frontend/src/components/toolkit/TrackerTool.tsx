"use client";

/**
 * Saved deadline tracker.
 *
 * The calculator answers once and is forgotten. This is the part that actually
 * prevents a right lapsing — the user pins a deadline to a matter of their own
 * and it counts down every time they come back.
 */

import { useCallback, useEffect, useState } from "react";
import { Check, Loader2, Plus, Trash2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/lib/auth/AuthProvider";
import {
  API,
  Label,
  SectionCard,
  buttonClass,
  formatDate,
  groupByCategory,
  inputClass,
  urgencyTone,
} from "./shared";

interface LimitationRule {
  id: string;
  label: string;
  category: string;
  trigger: string;
  has_limitation: boolean;
}

interface SavedDeadline {
  id: number;
  rule_label: string;
  citation: string | null;
  matter_reference: string | null;
  event_date: string;
  deadline_date: string;
  notes: string | null;
  completed: boolean;
  days_remaining: number;
  expired: boolean;
  urgency: keyof typeof urgencyTone;
}

export function TrackerTool({ onError }: { onError: (m: string | null) => void }) {
  const { user, ready, authHeader } = useAuth();
  const [rules, setRules] = useState<LimitationRule[]>([]);
  const [items, setItems] = useState<SavedDeadline[]>([]);
  const [loading, setLoading] = useState(true);
  const [adding, setAdding] = useState(false);
  const [busy, setBusy] = useState(false);

  const [ruleId, setRuleId] = useState("");
  const [eventDate, setEventDate] = useState("");
  const [reference, setReference] = useState("");

  const load = useCallback(async () => {
    if (!user) {
      setLoading(false);
      return;
    }
    try {
      const res = await fetch(`${API}/api/deadlines`, { headers: authHeader() });
      if (!res.ok) throw new Error("Could not load your deadlines");
      setItems(await res.json());
    } catch (e) {
      onError(e instanceof Error ? e.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }, [user, authHeader, onError]);

  useEffect(() => {
    if (!ready) return;
    load();
    fetch(`${API}/api/tools/limitation`)
      .then((r) => r.json())
      .then((d) => setRules((d.rules ?? []).filter((r: LimitationRule) => r.has_limitation)))
      .catch(() => undefined);
  }, [ready, load]);

  const save = async () => {
    setBusy(true);
    onError(null);
    try {
      const res = await fetch(`${API}/api/deadlines`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...authHeader() },
        body: JSON.stringify({
          rule_id: ruleId,
          event_date: eventDate,
          matter_reference: reference,
        }),
      });
      const json = await res.json();
      if (!res.ok) throw new Error(json.detail || "Could not save");
      setItems((prev) =>
        [...prev, json].sort((a, b) => a.deadline_date.localeCompare(b.deadline_date)),
      );
      setAdding(false);
      setRuleId("");
      setEventDate("");
      setReference("");
    } catch (e) {
      onError(e instanceof Error ? e.message : "Something went wrong");
    } finally {
      setBusy(false);
    }
  };

  const complete = async (id: number) => {
    await fetch(`${API}/api/deadlines/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json", ...authHeader() },
      body: JSON.stringify({ completed: true }),
    });
    setItems((prev) => prev.filter((d) => d.id !== id));
  };

  const remove = async (id: number) => {
    await fetch(`${API}/api/deadlines/${id}`, { method: "DELETE", headers: authHeader() });
    setItems((prev) => prev.filter((d) => d.id !== id));
  };

  if (!ready || loading) {
    return (
      <SectionCard>
        <div className="flex items-center gap-2 text-sm text-gray-500">
          <Loader2 className="h-4 w-4 animate-spin" />
          Loading…
        </div>
      </SectionCard>
    );
  }

  if (!user) {
    return (
      <SectionCard>
        <h2 className="font-serif text-xl font-bold text-slate-900">
          Sign in to track deadlines
        </h2>
        <p className="mt-2 max-w-prose text-sm text-gray-600">
          The calculator works without an account. Saving a deadline so it counts down
          across visits needs one, because it has to be stored against you.
        </p>
        <div className="mt-4 flex gap-3">
          <a href="/login" className={cn(buttonClass, "w-auto")}>
            Sign in
          </a>
          <a
            href="/register"
            className="flex items-center justify-center rounded-full border border-gray-200 px-6 py-3 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50"
          >
            Create an account
          </a>
        </div>
      </SectionCard>
    );
  }

  return (
    <div className="space-y-5">
      <SectionCard>
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="font-serif text-xl font-bold text-slate-900">Your deadlines</h2>
            <p className="mt-0.5 text-sm text-gray-500">
              {items.length === 0
                ? "Nothing tracked yet."
                : `${items.length} active, soonest first.`}
            </p>
          </div>
          <button
            onClick={() => setAdding((v) => !v)}
            className="flex items-center gap-1.5 rounded-full border border-gray-200 px-4 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50"
          >
            <Plus className="h-4 w-4" />
            Track a deadline
          </button>
        </div>

        {adding && (
          <div className="mt-5 space-y-4 border-t border-gray-100 pt-5">
            <div>
              <Label>What are you tracking?</Label>
              <select
                value={ruleId}
                onChange={(e) => setRuleId(e.target.value)}
                className={inputClass}
              >
                <option value="">Select a matter…</option>
                {groupByCategory(rules).map(([category, list]) => (
                  <optgroup key={category} label={category}>
                    {list.map((r) => (
                      <option key={r.id} value={r.id}>
                        {r.label}
                      </option>
                    ))}
                  </optgroup>
                ))}
              </select>
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <Label>Date the clock started</Label>
                <input
                  type="date"
                  value={eventDate}
                  max={new Date().toISOString().slice(0, 10)}
                  onChange={(e) => setEventDate(e.target.value)}
                  className={inputClass}
                />
              </div>
              <div>
                <Label>Your reference for this matter</Label>
                <input
                  type="text"
                  value={reference}
                  onChange={(e) => setReference(e.target.value)}
                  placeholder="e.g. Mehta — cheque 004512"
                  className={inputClass}
                />
              </div>
            </div>
            <button
              onClick={save}
              disabled={!ruleId || !eventDate || busy}
              className={buttonClass}
            >
              {busy ? <Loader2 className="h-4 w-4 animate-spin" /> : <Plus className="h-4 w-4" />}
              Save deadline
            </button>
          </div>
        )}
      </SectionCard>

      {items.map((d) => {
        const tone = urgencyTone[d.urgency] ?? urgencyTone.none;
        return (
          <div
            key={d.id}
            className={cn("rounded-2xl border p-5 animate-fade-in-up", tone.box)}
          >
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div className="min-w-0">
                {d.matter_reference && (
                  <p className="text-sm font-semibold text-gray-900">{d.matter_reference}</p>
                )}
                <p className={cn("text-sm", d.matter_reference ? "text-gray-600" : "font-semibold text-gray-900")}>
                  {d.rule_label}
                </p>
                <p className="mt-1.5 text-sm tabular-nums text-gray-700">
                  Due <strong>{formatDate(d.deadline_date)}</strong>
                </p>
                {d.citation && <p className="mt-1 text-xs text-gray-500">{d.citation}</p>}
              </div>

              <div className="flex shrink-0 items-center gap-3">
                <div className="text-right">
                  <p className={cn("text-2xl font-bold tabular-nums leading-none", tone.text)}>
                    {Math.abs(d.days_remaining)}
                  </p>
                  <p className={cn("text-xs", tone.text)}>
                    {d.expired ? "days overdue" : "days left"}
                  </p>
                </div>
                <div className="flex flex-col gap-1">
                  <button
                    onClick={() => complete(d.id)}
                    title="Mark as done"
                    aria-label={`Mark ${d.rule_label} as done`}
                    className="rounded-lg p-1.5 text-gray-400 transition-colors hover:bg-white hover:text-emerald-600"
                  >
                    <Check className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => remove(d.id)}
                    title="Remove"
                    aria-label={`Remove ${d.rule_label}`}
                    className="rounded-lg p-1.5 text-gray-400 transition-colors hover:bg-white hover:text-red-600"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
