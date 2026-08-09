"use client";

/** Pieces shared across the toolkit tools. */

import { cn } from "@/lib/utils";

export const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const inputClass =
  "w-full rounded-xl border border-gray-200 px-3.5 py-2.5 text-sm transition-colors " +
  "focus:border-transparent focus:outline-none focus:ring-2 focus:ring-black";

export const buttonClass =
  "flex w-full items-center justify-center gap-2 rounded-full bg-black px-6 py-3 " +
  "text-sm font-medium text-white transition-colors hover:bg-gray-800 " +
  "disabled:opacity-40 sm:w-auto";

export function SectionCard({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div className={cn("rounded-2xl border border-gray-200 bg-white p-5 sm:p-6", className)}>
      {children}
    </div>
  );
}

export function Label({ children }: { children: React.ReactNode }) {
  return <span className="mb-1.5 block text-sm font-medium text-gray-700">{children}</span>;
}

/** Group a flat list by its `category` field, preserving first-seen order. */
export function groupByCategory<T extends { category: string }>(items: T[]) {
  const map = new Map<string, T[]>();
  for (const item of items) {
    const list = map.get(item.category) ?? [];
    list.push(item);
    map.set(item.category, list);
  }
  return [...map.entries()];
}

export function formatDate(iso: string | null | undefined): string {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString("en-IN", {
    day: "numeric",
    month: "long",
    year: "numeric",
  });
}

/**
 * Urgency palette, shared so a countdown means the same thing everywhere in
 * the product. Colour is never the only signal — a number sits beside it.
 */
export const urgencyTone: Record<string, { box: string; text: string; dot: string }> = {
  expired: { box: "border-red-200 bg-red-50", text: "text-red-800", dot: "bg-red-500" },
  urgent: { box: "border-red-200 bg-red-50", text: "text-red-800", dot: "bg-red-500" },
  soon: { box: "border-amber-200 bg-amber-50", text: "text-amber-900", dot: "bg-amber-500" },
  comfortable: {
    box: "border-emerald-200 bg-emerald-50",
    text: "text-emerald-900",
    dot: "bg-emerald-500",
  },
  done: { box: "border-gray-200 bg-gray-50", text: "text-gray-500", dot: "bg-gray-400" },
  none: { box: "border-gray-200 bg-gray-50", text: "text-gray-700", dot: "bg-gray-400" },
};

/** POST helper that unwraps FastAPI's error shape. */
export async function postJSON<T>(
  path: string,
  body: unknown,
  headers: Record<string, string> = {},
): Promise<T> {
  const res = await fetch(`${API}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...headers },
    body: JSON.stringify(body),
  });
  const json = await res.json();
  if (!res.ok) throw new Error(json.detail || "Request failed");
  return json as T;
}
