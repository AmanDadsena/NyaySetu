"use client";

/**
 * Voice dictation via the Web Speech API.
 *
 * Chromium browsers stream audio to a cloud recogniser and support the Indian
 * language tags we care about (hi-IN, ta-IN, …). Firefox and most in-app
 * browsers don't implement `SpeechRecognition` at all, so `isSupported` is part
 * of the public API — callers hide the mic entirely rather than offering a
 * button that silently does nothing.
 */

import { useCallback, useEffect, useRef, useState } from "react";
import {
  getSpeechRecognitionCtor,
  type SpeechRecognitionErrorCode,
  type SpeechRecognitionEventLike,
  type SpeechRecognitionErrorEventLike,
  type SpeechRecognitionLike,
} from "./speech-types";

export type VoiceError = "unsupported" | "denied" | "no-speech" | "network" | "unknown";

interface Options {
  /** BCP-47 tag, e.g. "hi-IN". Changing it takes effect on the next start(). */
  lang: string;
  /** Called once with the final transcript when the user stops speaking. */
  onResult?: (transcript: string) => void;
  onError?: (error: VoiceError) => void;
}

interface SpeechRecognitionState {
  isSupported: boolean;
  isListening: boolean;
  /** Live partial transcript — useful for showing what's being heard. */
  interim: string;
  error: VoiceError | null;
  start: () => void;
  stop: () => void;
  toggle: () => void;
}

function mapError(code: SpeechRecognitionErrorCode): VoiceError {
  switch (code) {
    case "not-allowed":
    case "service-not-allowed":
      return "denied";
    case "no-speech":
      return "no-speech";
    case "network":
      return "network";
    case "aborted":
      // User-initiated stop; not worth surfacing.
      return "unknown";
    default:
      return "unknown";
  }
}

export function useSpeechRecognition({
  lang,
  onResult,
  onError,
}: Options): SpeechRecognitionState {
  const [isSupported, setIsSupported] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [interim, setInterim] = useState("");
  const [error, setError] = useState<VoiceError | null>(null);

  const recognitionRef = useRef<SpeechRecognitionLike | null>(null);
  const finalRef = useRef("");

  // Callbacks live in refs so that re-creating them each render doesn't tear
  // down and rebuild the recogniser mid-utterance.
  const onResultRef = useRef(onResult);
  const onErrorRef = useRef(onError);
  useEffect(() => {
    onResultRef.current = onResult;
    onErrorRef.current = onError;
  }, [onResult, onError]);

  // Support detection must happen after mount: on the server there is no
  // `window`, and rendering the mic during SSR would cause a hydration
  // mismatch on browsers that lack the API.
  useEffect(() => {
    setIsSupported(getSpeechRecognitionCtor() !== null);
  }, []);

  const stop = useCallback(() => {
    recognitionRef.current?.stop();
    setIsListening(false);
  }, []);

  const start = useCallback(() => {
    const Ctor = getSpeechRecognitionCtor();
    if (!Ctor) {
      setError("unsupported");
      onErrorRef.current?.("unsupported");
      return;
    }

    // Restarting a live recogniser throws; tear the old one down first.
    if (recognitionRef.current) {
      recognitionRef.current.abort();
      recognitionRef.current = null;
    }

    const recognition = new Ctor();
    recognition.lang = lang;
    recognition.interimResults = true;
    recognition.continuous = false;
    recognition.maxAlternatives = 1;

    finalRef.current = "";
    setInterim("");
    setError(null);

    recognition.onstart = () => setIsListening(true);

    recognition.onresult = (event: SpeechRecognitionEventLike) => {
      let interimText = "";
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i];
        const transcript = result[0].transcript;
        if (result.isFinal) {
          finalRef.current += transcript;
        } else {
          interimText += transcript;
        }
      }
      setInterim(interimText);
    };

    recognition.onerror = (event: SpeechRecognitionErrorEventLike) => {
      const mapped = mapError(event.error);
      if (event.error !== "aborted") {
        setError(mapped);
        onErrorRef.current?.(mapped);
      }
      setIsListening(false);
    };

    recognition.onend = () => {
      setIsListening(false);
      setInterim("");
      const text = finalRef.current.trim();
      if (text) onResultRef.current?.(text);
      finalRef.current = "";
    };

    recognitionRef.current = recognition;

    try {
      recognition.start();
    } catch {
      // Thrown when start() races an already-running session.
      setIsListening(false);
    }
  }, [lang]);

  const toggle = useCallback(() => {
    if (isListening) stop();
    else start();
  }, [isListening, start, stop]);

  // Abort any in-flight recognition when the component unmounts, otherwise the
  // mic indicator can stay lit after navigating away.
  useEffect(() => {
    return () => {
      recognitionRef.current?.abort();
      recognitionRef.current = null;
    };
  }, []);

  return { isSupported, isListening, interim, error, start, stop, toggle };
}
