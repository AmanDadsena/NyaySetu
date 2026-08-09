"use client";

/**
 * Read-aloud toggle for a block of text.
 *
 * Speech synthesis is far more widely supported than recognition, but the set
 * of *installed voices* varies by OS. When no voice matches the active locale
 * the button stays visible and says so, since the browser will often still
 * speak using a fallback voice.
 */

import { Volume2, VolumeX } from "lucide-react";
import { cn } from "@/lib/utils";
import { useLanguage } from "@/lib/i18n/LanguageProvider";
import { useSpeechSynthesis } from "@/lib/voice/useSpeechSynthesis";

interface SpeakButtonProps {
  /** Text to read. Markdown is stripped before speaking. */
  text: string;
  /** `icon` for inline use next to a message, `labelled` for a standalone control. */
  variant?: "icon" | "labelled";
  className?: string;
}

export function SpeakButton({ text, variant = "icon", className }: SpeakButtonProps) {
  const { t, meta } = useLanguage();
  const { isSupported, isSpeaking, hasVoiceForLang, toggle } = useSpeechSynthesis({
    lang: meta.speech,
  });

  if (!isSupported || !text.trim()) return null;

  const label = isSpeaking ? t("voice.stopReading") : t("voice.readAloud");
  const title = hasVoiceForLang
    ? label
    : `${label} (${meta.label}: no installed voice — your device may substitute another)`;

  if (variant === "labelled") {
    return (
      <button
        type="button"
        onClick={() => toggle(text)}
        aria-label={label}
        title={title}
        aria-pressed={isSpeaking}
        className={cn(
          "inline-flex items-center gap-1.5 rounded-full px-3 py-1.5 text-xs font-medium transition-colors",
          isSpeaking
            ? "bg-primary text-primary-foreground"
            : "bg-muted text-muted-foreground hover:bg-muted/80 hover:text-foreground",
          className,
        )}
      >
        {isSpeaking ? (
          <VolumeX className="h-3.5 w-3.5" />
        ) : (
          <Volume2 className="h-3.5 w-3.5" />
        )}
        {label}
      </button>
    );
  }

  return (
    <button
      type="button"
      onClick={() => toggle(text)}
      aria-label={label}
      title={title}
      aria-pressed={isSpeaking}
      className={cn(
        "inline-flex h-6 w-6 items-center justify-center rounded-full transition-colors",
        isSpeaking
          ? "bg-primary/15 text-primary"
          : "text-gray-400 hover:bg-gray-100 hover:text-gray-700",
        className,
      )}
    >
      {isSpeaking ? <VolumeX className="h-3.5 w-3.5" /> : <Volume2 className="h-3.5 w-3.5" />}
    </button>
  );
}
