"use client";

/**
 * Microphone button that dictates into a text field.
 *
 * Renders nothing when the browser has no SpeechRecognition implementation —
 * a dead mic is worse than no mic for the users this is aimed at.
 */

import { Mic, Square } from "lucide-react";
import { cn } from "@/lib/utils";
import { useLanguage } from "@/lib/i18n/LanguageProvider";
import { useSpeechRecognition, type VoiceError } from "@/lib/voice/useSpeechRecognition";
import type { TranslationKey } from "@/lib/i18n/translations";

interface VoiceButtonProps {
  /** Receives the final transcript once the user stops speaking. */
  onTranscript: (text: string) => void;
  onError?: (message: string) => void;
  /** Translation key for the idle label — lets each surface name its own action. */
  idleLabelKey?: TranslationKey;
  /** Shown while listening, next to the button. */
  showInterim?: boolean;
  disabled?: boolean;
  className?: string;
}

export function VoiceButton({
  onTranscript,
  onError,
  idleLabelKey = "voice.speak",
  showInterim = false,
  disabled = false,
  className,
}: VoiceButtonProps) {
  const { t, meta } = useLanguage();

  const errorMessage = (error: VoiceError): string => {
    if (error === "denied") return t("voice.micDenied");
    if (error === "no-speech") return t("voice.noSpeech");
    if (error === "unsupported") return t("voice.unsupported");
    return t("voice.noSpeech");
  };

  const { isSupported, isListening, interim, toggle } = useSpeechRecognition({
    lang: meta.speech,
    onResult: onTranscript,
    onError: (error) => onError?.(errorMessage(error)),
  });

  if (!isSupported) return null;

  const label = isListening ? t("voice.stopListening") : t(idleLabelKey);

  return (
    <div className="flex items-center gap-2">
      {showInterim && isListening && interim && (
        <span className="text-xs text-muted-foreground truncate max-w-[160px]">
          {interim}
        </span>
      )}
      <button
        type="button"
        onClick={toggle}
        disabled={disabled}
        aria-label={label}
        title={label}
        aria-pressed={isListening}
        className={cn(
          "relative flex items-center justify-center rounded-full transition-colors",
          "h-9 w-9 shrink-0 disabled:opacity-40 disabled:cursor-not-allowed",
          isListening
            ? "bg-red-500 text-white hover:bg-red-600"
            : "bg-gray-100 text-gray-600 hover:bg-gray-200 hover:text-gray-900",
          className,
        )}
      >
        {isListening && (
          <span className="absolute inset-0 rounded-full bg-red-500/40 animate-ping" />
        )}
        <span className="relative">
          {isListening ? (
            <Square className="h-3.5 w-3.5 fill-current" />
          ) : (
            <Mic className="h-4 w-4" />
          )}
        </span>
      </button>
    </div>
  );
}
