"use client";

/**
 * The site's heartbeat.
 *
 * This asks the running backend what it actually has — `/api/bot/health`
 * returns the live passage count, whether dense retrieval loaded, and whether
 * the service considers itself ready — and reports the answer. It replaced a
 * hardcoded "142 Lawyers / 94% Match Rate" panel that was true of nothing.
 *
 * The honesty rule it follows: **when the backend cannot be reached, say so.**
 * It never falls back to printing a plausible number, because a figure that
 * appears whether or not the system is up is not a status indicator, it is
 * decoration. The static figures elsewhere on the page are clearly labelled as
 * corpus facts; this one is clearly labelled as right now.
 *
 * The unreachable state is not rare. The backend is a free Hugging Face Space
 * that sleeps when idle and takes the better part of a minute to wake, so the
 * first visitor after a quiet spell will see it — which is why it is written
 * as a calm, expected state rather than an error.
 */

import { useEffect, useState } from "react";
import { Activity, Database, Languages, WifiOff } from "lucide-react";
import { CORPUS_STATS } from "@/lib/site-stats";
import { cn } from "@/lib/utils";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/** Shape of `GET /api/bot/health` — see backend/app/routers/bot.py. */
interface Health {
  passages: number;
  dense_retrieval: boolean;
  status: string;
}

type State =
  | { kind: "checking" }
  | { kind: "online"; health: Health }
  | { kind: "unreachable" };

/** Long enough for a sleeping Space to wake, short enough not to hang forever. */
const TIMEOUT_MS = 15_000;

export function LiveStatus({ className }: { className?: string }) {
  const [state, setState] = useState<State>({ kind: "checking" });

  useEffect(() => {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);

    fetch(`${API}/api/bot/health`, { signal: controller.signal })
      .then((res) => (res.ok ? res.json() : Promise.reject(new Error(String(res.status)))))
      .then((health: Health) => setState({ kind: "online", health }))
      .catch(() => setState({ kind: "unreachable" }))
      .finally(() => clearTimeout(timer));

    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, []);

  return (
    <div
      // Announced to screen readers when it resolves, but politely — this is
      // ambient information, not something to interrupt anyone for.
      role="status"
      aria-live="polite"
      className={cn(
        "inline-flex flex-wrap items-center justify-center gap-x-5 gap-y-2 rounded-full border px-5 py-2.5 text-sm backdrop-blur-xl transition-colors duration-500",
        state.kind === "online"
          ? "border-emerald-200/70 bg-emerald-50/70 text-emerald-900"
          : state.kind === "unreachable"
            ? "border-gray-200 bg-gray-50/80 text-gray-600"
            : "border-gray-200 bg-white/70 text-gray-500",
        className,
      )}
    >
      {state.kind === "checking" && (
        <span className="flex items-center gap-2">
          <span className="h-2 w-2 shrink-0 animate-pulse rounded-full bg-gray-400" />
          <span>Checking the assistant…</span>
        </span>
      )}

      {state.kind === "unreachable" && (
        <span className="flex items-center gap-2">
          <WifiOff className="h-4 w-4 shrink-0" aria-hidden="true" />
          <span>
            Assistant offline — the toolkit below still works
          </span>
        </span>
      )}

      {state.kind === "online" && (
        <>
          <span className="flex items-center gap-2 font-medium">
            <span
              className="h-2 w-2 shrink-0 rounded-full bg-emerald-500 text-emerald-500 animate-live-pulse"
              aria-hidden="true"
            />
            <span>Retrieval online</span>
          </span>

          <span className="flex items-center gap-1.5 text-emerald-800/80">
            <Database className="h-3.5 w-3.5 shrink-0" aria-hidden="true" />
            <span className="tabular-nums">{state.health.passages}</span> provisions indexed
          </span>

          <span className="flex items-center gap-1.5 text-emerald-800/80">
            <Languages className="h-3.5 w-3.5 shrink-0" aria-hidden="true" />
            {CORPUS_STATS.languages.value} languages
          </span>

          {/* Dense retrieval is optional — it fuses embeddings with BM25 when
              the model is present. Saying which mode is running is more useful
              than implying there is only one. */}
          <span className="flex items-center gap-1.5 text-emerald-800/80">
            <Activity className="h-3.5 w-3.5 shrink-0" aria-hidden="true" />
            {state.health.dense_retrieval ? "hybrid search" : "keyword search"}
          </span>
        </>
      )}
    </div>
  );
}
