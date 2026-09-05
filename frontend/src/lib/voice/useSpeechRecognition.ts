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

export interface SpeechRecognitionState {
  isSupported: boolean;
  isListening: boolean;
  /** Live partial transcript — useful for showing what's being heard. */
  interim: string;
  /** Normalized mic input volume level (0.0 to 1.0) for driving visualizers. */
  audioLevel: number;
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
  const [audioLevel, setAudioLevel] = useState(0);
  const [error, setError] = useState<VoiceError | null>(null);

  const recognitionRef = useRef<SpeechRecognitionLike | null>(null);
  const finalRef = useRef("");
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const animFrameRef = useRef<number | null>(null);

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

  const stopAudioAnalysis = useCallback(() => {
    if (animFrameRef.current !== null) {
      cancelAnimationFrame(animFrameRef.current);
      animFrameRef.current = null;
    }
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach((t) => t.stop());
      mediaStreamRef.current = null;
    }
    if (audioContextRef.current && audioContextRef.current.state !== "closed") {
      audioContextRef.current.close().catch(() => {});
      audioContextRef.current = null;
    }
    setAudioLevel(0);
  }, []);

  const startAudioAnalysis = useCallback(async () => {
    try {
      if (typeof window === "undefined" || !navigator.mediaDevices?.getUserMedia) return;
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });
      mediaStreamRef.current = stream;

      const AudioCtx = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
      if (!AudioCtx) return;
      const ctx = new AudioCtx();
      audioContextRef.current = ctx;

      const analyser = ctx.createAnalyser();
      analyser.fftSize = 64;
      analyser.smoothingTimeConstant = 0.5;
      analyserRef.current = analyser;

      const source = ctx.createMediaStreamSource(stream);
      source.connect(analyser);

      const buffer = new Uint8Array(analyser.frequencyBinCount);
      const updateLevel = () => {
        analyser.getByteFrequencyData(buffer);
        let sum = 0;
        for (let i = 0; i < buffer.length; i++) sum += buffer[i];
        const avg = sum / buffer.length;
        // Normalize 0..255 to 0..1 with a sensitivity curve
        const norm = Math.min(1, avg / 128);
        setAudioLevel(norm);
        animFrameRef.current = requestAnimationFrame(updateLevel);
      };
      updateLevel();
    } catch {
      // Audio stream analysis is progressive enhancement; speech recognition can continue
    }
  }, []);

  const stop = useCallback(() => {
    recognitionRef.current?.stop();
    stopAudioAnalysis();
    setIsListening(false);
  }, [stopAudioAnalysis]);

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

    recognition.onstart = () => {
      setIsListening(true);
      startAudioAnalysis();
    };

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
      stopAudioAnalysis();
      setIsListening(false);
    };

    recognition.onend = () => {
      stopAudioAnalysis();
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
      stopAudioAnalysis();
      setIsListening(false);
    }
  }, [lang, startAudioAnalysis, stopAudioAnalysis]);

  const toggle = useCallback(() => {
    if (isListening) stop();
    else start();
  }, [isListening, start, stop]);

  // Abort any in-flight recognition when the component unmounts
  useEffect(() => {
    return () => {
      recognitionRef.current?.abort();
      recognitionRef.current = null;
      stopAudioAnalysis();
    };
  }, [stopAudioAnalysis]);

  return { isSupported, isListening, interim, audioLevel, error, start, stop, toggle };
}
