"use client";

/**
 * Read-aloud via `speechSynthesis` with multi-voice support.
 *
 * Features:
 *  1. Discovers and categorizes all available system voices for the selected locale.
 *  2. Supports user selection between multiple voices (e.g. Male/Female, natural).
 *  3. Configurable speech rate and pitch with localStorage persistence.
 *  4. Splits long responses into natural sentence-sized chunks to bypass Chromium's 15s cutoff.
 *  5. Cleans markdown and decorative legal symbols before reading.
 */

import { useCallback, useEffect, useMemo, useRef, useState } from "react";

interface Options {
  /** BCP-47 tag, e.g. "ta-IN", "hi-IN". */
  lang: string;
}

export interface SpeechSynthesisState {
  isSupported: boolean;
  isSpeaking: boolean;
  /** True when at least one installed voice matches `lang`. */
  hasVoiceForLang: boolean;
  /** All voices available on the device for the current language. */
  availableVoices: SpeechSynthesisVoice[];
  /** The currently chosen voice. */
  selectedVoice: SpeechSynthesisVoice | null;
  /** Select a specific voice by instance or voiceURI. */
  setSelectedVoice: (voice: SpeechSynthesisVoice | string) => void;
  /** Speech rate (0.75 - 1.5). Default 0.95. */
  rate: number;
  setRate: (rate: number) => void;
  /** Speech pitch (0.5 - 1.5). Default 1.0. */
  pitch: number;
  setPitch: (pitch: number) => void;
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
  const [selectedVoiceURI, setSelectedVoiceURI] = useState<string | null>(null);
  const [rate, setRateState] = useState<number>(0.95);
  const [pitch, setPitchState] = useState<number>(1.0);

  // Set when we deliberately cancel, so the queue runner knows not to continue.
  const cancelledRef = useRef(false);

  useEffect(() => {
    if (typeof window === "undefined" || !("speechSynthesis" in window)) return;
    setIsSupported(true);

    const load = () => {
      const v = window.speechSynthesis.getVoices();
      if (v.length > 0) setVoices(v);
    };

    load();
    window.speechSynthesis.addEventListener("voiceschanged", load);
    return () => window.speechSynthesis.removeEventListener("voiceschanged", load);
  }, []);

  // Filter voices matching the current target language
  const availableVoices = useMemo(() => {
    const primary = lang.split("-")[0].toLowerCase();
    const normalizedTarget = lang.replace("_", "-").toLowerCase();

    return voices.filter((v) => {
      const vLang = v.lang.replace("_", "-").toLowerCase();
      return (
        vLang === normalizedTarget ||
        vLang.startsWith(primary + "-") ||
        vLang.startsWith(primary)
      );
    });
  }, [voices, lang]);

  // Load saved preference for this language if present
  useEffect(() => {
    if (typeof window === "undefined") return;
    try {
      const primary = lang.split("-")[0].toLowerCase();
      const savedURI = localStorage.getItem(`nyaysetu_voice_${primary}`);
      if (savedURI) {
        setSelectedVoiceURI(savedURI);
      } else {
        setSelectedVoiceURI(null);
      }
      const savedRate = localStorage.getItem("nyaysetu_voice_rate");
      if (savedRate) setRateState(Number(savedRate) || 0.95);
    } catch {
      // localStorage may fail in sandboxed iframes
    }
  }, [lang]);

  // Set and persist speech rate
  const setRate = useCallback((newRate: number) => {
    const clamped = Math.max(0.7, Math.min(1.5, newRate));
    setRateState(clamped);
    try {
      localStorage.setItem("nyaysetu_voice_rate", String(clamped));
    } catch {}
  }, []);

  // Set and persist pitch
  const setPitch = useCallback((newPitch: number) => {
    const clamped = Math.max(0.5, Math.min(1.5, newPitch));
    setPitchState(clamped);
  }, []);

  // Resolve active voice
  const selectedVoice = useMemo(() => {
    if (availableVoices.length === 0) return null;
    if (selectedVoiceURI) {
      const match = availableVoices.find((v) => v.voiceURI === selectedVoiceURI);
      if (match) return match;
    }
    // Default: prefer default voice, or first available
    return availableVoices.find((v) => v.default) ?? availableVoices[0];
  }, [availableVoices, selectedVoiceURI]);

  // Custom setter for choosing voice
  const setSelectedVoice = useCallback(
    (voiceOrUri: SpeechSynthesisVoice | string) => {
      const uri = typeof voiceOrUri === "string" ? voiceOrUri : voiceOrUri.voiceURI;
      setSelectedVoiceURI(uri);
      try {
        const primary = lang.split("-")[0].toLowerCase();
        localStorage.setItem(`nyaysetu_voice_${primary}`, uri);
      } catch {}
    },
    [lang],
  );

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
        if (selectedVoice) utterance.voice = selectedVoice;
        utterance.rate = rate;
        utterance.pitch = pitch;

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
    [lang, selectedVoice, rate, pitch],
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
    hasVoiceForLang: availableVoices.length > 0,
    availableVoices,
    selectedVoice,
    setSelectedVoice,
    rate,
    setRate,
    pitch,
    setPitch,
    speak,
    stop,
    toggle,
  };
}
