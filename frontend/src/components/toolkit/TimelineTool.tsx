"use client";

/**
 * Case timeline.
 *
 * The diary work a litigator otherwise does by hand for every matter. Stages
 * are marked by whether the period is a statutory bar or a directory target,
 * because that distinction is the whole value: a lawyer needs to know which
 * dates the court can forgive and which it cannot.
 */

import { useEffect, useMemo, useState } from "react";
import { CalendarDays, Loader2, Lock, Timer } from "lucide-react";
import { cn } from "@/lib/utils";
import {
  API,
  Label,
  SectionCard,
  buttonClass,
  formatDate,
  groupByCategory,
  inputClass,
  postJSON,
} from "./shared";

interface MatterType {
  id: string;
  label: string;
  category: string;
  start_label: string;
  stage_count: number;
  optional_anchors: { key: string; label: string }[];
}

interface Entry {
  key: string;
  label: string;
  nature: "statutory" | "directory" | "practical";
  authority: string;
  note: string;
  date: string | null;
  days_away: number | null;
  status: "scheduled" | "pending" | "passed";
  awaiting: string | null;
}

interface TimelineResult {
  label: string;
  start_label: string;
  start_date: string;
  entries: Entry[];
}

const NATURE_STYLE: Record<Entry["nature"], { chip: string; label: string; icon: typeof Lock }> = {
  statutory: {
    chip: "bg-red-50 text-red-700 border-red-200",
    label: "Statutory",
    icon: Lock,
  },
  directory: {
    chip: "bg-amber-50 text-amber-800 border-amber-200",
    label: "Directory",
    icon: Timer,
  },
  practical: {
    chip: "bg-gray-50 text-gray-600 border-gray-200",
    label: "In practice",
    icon: CalendarDays,
  },
};

export function TimelineTool({ onError }: { onError: (m: string | null) => void }) {
  const [matters, setMatters] = useState<MatterType[]>([]);
  const [matterId, setMatterId] = useState("");
  const [startDate, setStartDate] = useState("");
  const [known, setKnown] = useState<Record<string, string>>({});
  const [result, setResult] = useState<TimelineResult | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    fetch(`${API}/api/tools/timeline`)
      .then((r) => r.json())
      .then((d) => setMatters(d.matters ?? []))
      .catch(() => onError("Could not load matter types."));
  }, [onError]);

  const matter = useMemo(
    () => matters.find((m) => m.id === matterId) ?? null,
    [matters, matterId],
  );

  const run = async () => {
    setBusy(true);
    onError(null);
    try {
      setResult(
        await postJSON<TimelineResult>("/api/tools/timeline", {
          matter_id: matterId,
          start_date: startDate,
          known,
        }),
      );
    } catch (e) {
      onError(e instanceof Error ? e.message : "Something went wrong");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="space-y-5">
      <SectionCard>
        <div className="space-y-4">
          <div>
            <Label>What kind of matter?</Label>
            <select
              value={matterId}
              onChange={(e) => {
                setMatterId(e.target.value);
                setKnown({});
                setResult(null);
              }}
              className={inputClass}
            >
              <option value="">Select…</option>
              {groupByCategory(matters).map(([category, items]) => (
                <optgroup key={category} label={category}>
                  {items.map((m) => (
                    <option key={m.id} value={m.id}>
                      {m.label}
                    </option>
                  ))}
                </optgroup>
              ))}
            </select>
          </div>

          {matter && (
            <>
              <div>
                <Label>{matter.start_label}</Label>
                <input
                  type="date"
                  value={startDate}
                  onChange={(e) => {
                    setStartDate(e.target.value);
                    setResult(null);
                  }}
                  className={inputClass}
                />
              </div>

              {matter.optional_anchors.length > 0 && (
                <details className="rounded-xl border border-gray-200 bg-gray-50 px-4 py-3">
                  <summary className="cursor-pointer text-sm font-medium text-gray-700">
                    Already in progress? Add dates you know
                    <span className="ml-1 font-normal text-gray-500">
                      ({matter.optional_anchors.length} optional)
                    </span>
                  </summary>
                  <p className="mt-2 text-xs text-gray-500">
                    Later stages depend on events that have not happened yet. Fill in
                    any that have, and their downstream dates will be calculated too.
                  </p>
                  <div className="mt-3 grid gap-3 sm:grid-cols-2">
                    {matter.optional_anchors.map((a) => (
                      <div key={a.key}>
                        <Label>{a.label}</Label>
                        <input
                          type="date"
                          value={known[a.key] ?? ""}
                          onChange={(e) =>
                            setKnown((p) => ({ ...p, [a.key]: e.target.value }))
                          }
                          className={inputClass}
                        />
                      </div>
                    ))}
                  </div>
                </details>
              )}

              <button onClick={run} disabled={!startDate || busy} className={buttonClass}>
                {busy ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <CalendarDays className="h-4 w-4" />
                )}
                Build timeline
              </button>
            </>
          )}
        </div>
      </SectionCard>

      {result && (
        <SectionCard className="animate-fade-in-up">
          <h2 className="font-serif text-xl font-bold text-slate-900">{result.label}</h2>
          <p className="mt-1 text-sm text-gray-500">
            {result.start_label}: {formatDate(result.start_date)}
          </p>

          <div className="mt-5 flex flex-wrap gap-3 text-xs text-gray-500">
            <span className="flex items-center gap-1.5">
              <Lock className="h-3.5 w-3.5 text-red-500" /> Statutory — the court cannot excuse it
            </span>
            <span className="flex items-center gap-1.5">
              <Timer className="h-3.5 w-3.5 text-amber-500" /> Directory — a target, routinely exceeded
            </span>
          </div>

          {/* The rail makes the sequence legible; each stage hangs off it. */}
          <ol className="relative mt-5 space-y-0 border-l-2 border-gray-100 pl-6">
            {result.entries.map((entry) => {
              const style = NATURE_STYLE[entry.nature];
              const Icon = style.icon;
              const overdue = entry.status === "passed";
              return (
                <li key={entry.key} className="relative pb-6 last:pb-0">
                  <span
                    className={cn(
                      "absolute -left-[31px] flex h-4 w-4 items-center justify-center rounded-full border-2 border-white",
                      entry.status === "pending"
                        ? "bg-gray-300"
                        : overdue
                          ? "bg-gray-400"
                          : entry.nature === "statutory"
                            ? "bg-red-500"
                            : "bg-amber-500",
                    )}
                  />
                  <div className="flex flex-wrap items-baseline gap-x-2 gap-y-1">
                    <h3 className="text-sm font-semibold text-gray-900">{entry.label}</h3>
                    <span
                      className={cn(
                        "inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide",
                        style.chip,
                      )}
                    >
                      <Icon className="h-2.5 w-2.5" />
                      {style.label}
                    </span>
                  </div>

                  {entry.date ? (
                    <p
                      className={cn(
                        "mt-1 text-sm tabular-nums",
                        overdue ? "text-gray-400 line-through" : "font-medium text-gray-800",
                      )}
                    >
                      {formatDate(entry.date)}
                      {entry.days_away !== null && !overdue && (
                        <span className="ml-2 font-normal text-gray-500">
                          in {entry.days_away} days
                        </span>
                      )}
                    </p>
                  ) : (
                    <p className="mt-1 text-sm italic text-gray-500">
                      Waiting on {entry.awaiting}
                    </p>
                  )}

                  {entry.note && (
                    <p className="mt-1.5 text-xs leading-relaxed text-gray-600">{entry.note}</p>
                  )}
                  {entry.authority && (
                    <p className="mt-1 text-[11px] text-gray-400">{entry.authority}</p>
                  )}
                </li>
              );
            })}
          </ol>
        </SectionCard>
      )}
    </div>
  );
}
