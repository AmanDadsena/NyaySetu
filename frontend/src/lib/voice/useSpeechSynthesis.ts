"use client";

/**
 * Read-aloud via `speechSynthesis`.
 *
 * Two browser quirks shape this implementation:
 *
 *  1. `getVoices()` is populated asynchronously and returns `[]` on first call
 *     in Chromium, so we also listen for `voiceschanged`.
 *  2. Chromium silently stops speaking after roughly fifteen seconds of a
 *     single utterance. Splitting the text into sentence-sized utterances and
 *     queueing them keeps long analysis summaries audible to the end.
 */

import { useCallback, useEffect, useRef, useState } from "react";

interface Options {
  /** BCP-47 tag, e.g. "ta-IN". */
  lang: string;
}

interface SpeechSynthesisState {
  isSupported: boolean;
  isSpeaking: boolean;
  /** True when no installed voice matches `lang`; audio may fall back or be silent. */
  hasVoiceForLang: boolean;
  speak: (text: string) => void;
  stop: () => void;
  toggle: (text: string) => void;
}

/** Characters that carry meaning on screen but only add noise when spoken. */
const MARKDOWN_NOISE = /(\*\*|__|\*|`|#{1,6}\s|>\s|\[|\]|\(|\))/g;

/**
 * Strip markdown and decorative glyphs so the voice reads prose, not syntax.
 * Without this the assistant literally says "asterisk asterisk" around every
 * bold heading in the legal answers.
 */
export function textToSpeak(markdown: string): string {
  return markdown
    .replace(/\[([^\]]+)\]\([^)]*\)/g, "$1") // links → their label
    .replace(MARKDOWN_NOISE, " ")
    // Decorative glyphs: some engines announce these by name ("warning sign").
    .replace(/[•·→]/gu, " ")
    .replace(/\p{Extended_Pictographic}️?/gu, " ")
    .replace(/\s+/g, " ")
    .trim();
}

/**
 * Break text into utterance-sized chunks, preferring sentence boundaries.
 * Danda (।) is the sentence terminator in Devanagari-script languages.
 */
function chunkForSpeech(text: string, maxChars = 180): string[] {
  const sentences = text.split(/(?<=[.!?।])\s+/);
  const chunks: string[] = [];
  let current = "";

  for (const sentence of sentences) {
    if (!current) {
      current = sentence;
    } else if (current.length + sentence.length + 1 <= maxChars) {
      current += " " + sentence;
    } else {
      chunks.push(current);
      current = sentence;
    }
  }
  if (current) chunks.push(current);

  // A single sentence can still exceed the limit; split it on width.
  return chunks.flatMap((chunk) => {
    if (chunk.length <= maxChars * 2) return [chunk];
    const parts: string[] = [];
    for (let i = 0; i < chunk.length; i += maxChars) {
      parts.push(chunk.slice(i, i + maxChars));
    }
    return parts;
  });
}

export function useSpeechSynthesis({ lang }: Options): SpeechSynthesisState {
  const [isSupported, setIsSupported] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [voices, setVoices] = useState<SpeechSynthesisVoice[]>([]);

  // Set when we deliberately cancel, so the queue runner knows not to continue.
  const cancelledRef = useRef(false);

  useEffect(() => {
    if (typeof window === "undefined" || !("speechSynthesis" in window)) return;
    setIsSupported(true);

    const load = () => setVoices(window.speechSynthesis.getVoices());
    load();
    window.speechSynthesis.addEventListener("voiceschanged", load);
    return () => window.speechSynthesis.removeEventListener("voiceschanged", load);
  }, []);

  const primary = lang.split("-")[0];
  const voiceForLang =
    voices.find((v) => v.lang.replace("_", "-") === lang) ??
    voices.find((v) => v.lang.replace("_", "-").startsWith(primary + "-")) ??
    voices.find((v) => v.lang.startsWith(primary)) ??
    null;

  const stop = useCallback(() => {
    if (typeof window === "undefined" || !("speechSynthesis" in window)) return;
    cancelledRef.current = true;
    window.speechSynthesis.cancel();
    setIsSpeaking(false);
  }, []);

  const speak = useCallback(
    (raw: string) => {
      if (typeof window === "undefined" || !("speechSynthesis" in window)) return;

      const clean = textToSpeak(raw);
      if (!clean) return;

      // Cancel anything already queued, then start fresh.
      window.speechSynthesis.cancel();
      cancelledRef.current = false;

      const chunks = chunkForSpeech(clean);
      let index = 0;

      const speakNext = () => {
        if (cancelledRef.current || index >= chunks.length) {
          setIsSpeaking(false);
          return;
        }

        const utterance = new SpeechSynthesisUtterance(chunks[index]);
        utterance.lang = lang;
        if (voiceForLang) utterance.voice = voiceForLang;
        // Indian-language voices are easier to follow slightly below default
        // rate, which matters for the low-literacy users this targets.
        utterance.rate = 0.95;
        utterance.pitch = 1;

        utterance.onend = () => {
          index += 1;
          speakNext();
        };
        utterance.onerror = () => {
          setIsSpeaking(false);
        };

        window.speechSynthesis.speak(utterance);
      };

      setIsSpeaking(true);
      speakNext();
    },
    [lang, voiceForLang],
  );

  const toggle = useCallback(
    (text: string) => {
      if (isSpeaking) stop();
      else speak(text);
    },
    [isSpeaking, speak, stop],
  );

  // Speech continues playing after unmount unless explicitly cancelled.
  useEffect(() => {
    return () => {
      if (typeof window !== "undefined" && "speechSynthesis" in window) {
        window.speechSynthesis.cancel();
      }
    };
  }, []);

  return {
    isSupported,
    isSpeaking,
    hasVoiceForLang: voiceForLang !== null,
    speak,
    stop,
    toggle,
  };
}
