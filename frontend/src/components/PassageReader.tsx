"use client";

/**
 * Reveals the exact corpus passage an answer was built from.
 *
 * The citation beside this already links out, but for most of the corpus that
 * link is India Code's front page: it proves the Act exists, not that it says
 * what the answer claims. This closes that gap by showing the passage itself —
 * the same text the retriever handed the model — so a reader can compare the
 * claim against its source without leaving the conversation or trusting us.
 *
 * Fetched on first open rather than with the answer. Most people never expand
 * a citation, and sending three full passages with every reply would slow the
 * thing that matters, which is time to first word.
 */

import { useCallback, useState } from "react";
import { ChevronDown, Loader2 } from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Passage {
  id: string;
  title: string;
  citation: string;
  text: string;
  url: string;
}

export function PassageReader({ id, label }: { id: string; label: string }) {
  const [open, setOpen] = useState(false);
  const [passage, setPassage] = useState<Passage | null>(null);
  const [busy, setBusy] = useState(false);
  const [failed, setFailed] = useState(false);

  const toggle = useCallback(async () => {
    if (open) {
      setOpen(false);
      return;
    }
    setOpen(true);
    if (passage || busy) return;

    setBusy(true);
    setFailed(false);
    try {
      const res = await fetch(`${API}/api/bot/passage/${encodeURIComponent(id)}`);
      if (!res.ok) throw new Error("not found");
      setPassage((await res.json()) as Passage);
    } catch {
      setFailed(true);
    } finally {
      setBusy(false);
    }
  }, [id, open, passage, busy]);

  return (
    <span className="chatbot-passage">
      <button
        type="button"
        onClick={toggle}
        aria-expanded={open}
        className="chatbot-passage-toggle"
      >
        {busy ? (
          <Loader2 className="h-3 w-3 animate-spin" aria-hidden />
        ) : (
          <ChevronDown
            className={`h-3 w-3 transition-transform ${open ? "rotate-180" : ""}`}
            aria-hidden
          />
        )}
        {label}
      </button>

      {open && passage && (
        <span className="chatbot-passage-body">
          <strong>{passage.title}</strong>
          <em>{passage.citation}</em>
          {passage.text}
        </span>
      )}

      {open && failed && (
        <span className="chatbot-passage-body">
          Could not load this provision right now.
        </span>
      )}
    </span>
  );
}
