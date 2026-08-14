/**
 * Locale registry.
 *
 * Every supported language is described once, here. Each entry carries the
 * three different identifiers the app needs for the same language:
 *
 *  - `code`   — short key used in the cookie, the URL and the translation maps
 *  - `speech` — BCP-47 tag handed to the Web Speech API for dictation / read-aloud
 *  - `gemini` — plain-English language name the backend puts into the AI prompt
 *
 * The set intentionally matches the languages the analyze endpoint already
 * supported, so the global switcher and the analyze dropdown never disagree.
 */

export interface LocaleMeta {
  code: LocaleCode;
  /** English name, for accessibility labels and the backend. */
  label: string;
  /** Endonym — how speakers write the language in their own script. */
  native: string;
  /** BCP-47 tag for SpeechRecognition / SpeechSynthesis. */
  speech: string;
  /** Language name sent to the backend for AI output. */
  gemini: string;
}

export const LOCALE_CODES = [
  "en",
  "hi",
  "mr",
  "gu",
  "ta",
  "te",
  "bn",
  "kn",
] as const;

export type LocaleCode = (typeof LOCALE_CODES)[number];

export const DEFAULT_LOCALE: LocaleCode = "en";

export const LOCALES: Record<LocaleCode, LocaleMeta> = {
  en: { code: "en", label: "English", native: "English", speech: "en-IN", gemini: "English" },
  hi: { code: "hi", label: "Hindi", native: "हिन्दी", speech: "hi-IN", gemini: "Hindi" },
  mr: { code: "mr", label: "Marathi", native: "मराठी", speech: "mr-IN", gemini: "Marathi" },
  gu: { code: "gu", label: "Gujarati", native: "ગુજરાતી", speech: "gu-IN", gemini: "Gujarati" },
  ta: { code: "ta", label: "Tamil", native: "தமிழ்", speech: "ta-IN", gemini: "Tamil" },
  te: { code: "te", label: "Telugu", native: "తెలుగు", speech: "te-IN", gemini: "Telugu" },
  bn: { code: "bn", label: "Bengali", native: "বাংলা", speech: "bn-IN", gemini: "Bengali" },
  kn: { code: "kn", label: "Kannada", native: "ಕನ್ನಡ", speech: "kn-IN", gemini: "Kannada" },
};

export const LOCALE_LIST: LocaleMeta[] = LOCALE_CODES.map((c) => LOCALES[c]);

/** Cookie the server layout reads so the first paint is already in-language. */
export const LOCALE_COOKIE = "nyaysetu_locale";

/** Narrow an untrusted string (cookie, query param) to a supported locale. */
export function normalizeLocale(value: string | undefined | null): LocaleCode {
  if (!value) return DEFAULT_LOCALE;
  const lower = value.toLowerCase();
  if ((LOCALE_CODES as readonly string[]).includes(lower)) {
    return lower as LocaleCode;
  }
  // Accept full tags such as "hi-IN" by falling back to the primary subtag.
  const primary = lower.split("-")[0];
  if ((LOCALE_CODES as readonly string[]).includes(primary)) {
    return primary as LocaleCode;
  }
  return DEFAULT_LOCALE;
}
