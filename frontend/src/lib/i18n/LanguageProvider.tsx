"use client";

/**
 * Global language context.
 *
 * The chosen locale is persisted in a cookie rather than localStorage so the
 * *server* can read it in the root layout and render the very first paint in
 * the right language. Reading it on the client instead would leave non-English
 * users staring at a flash of English on every hard navigation — exactly the
 * users this feature exists for.
 */

import React, {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
} from "react";
import {
  DEFAULT_LOCALE,
  LOCALES,
  LOCALE_COOKIE,
  type LocaleCode,
  type LocaleMeta,
} from "./locales";
import { translate, type TranslationKey } from "./translations";

interface LanguageContextValue {
  locale: LocaleCode;
  meta: LocaleMeta;
  setLocale: (next: LocaleCode) => void;
  /** Translate a key into the active locale, falling back to English. */
  t: (key: TranslationKey) => string;
}

const LanguageContext = createContext<LanguageContextValue | null>(null);

const ONE_YEAR_SECONDS = 60 * 60 * 24 * 365;

function persistLocale(locale: LocaleCode) {
  try {
    document.cookie = `${LOCALE_COOKIE}=${locale}; path=/; max-age=${ONE_YEAR_SECONDS}; samesite=lax`;
  } catch {
    // Cookies disabled — the choice simply won't survive a reload.
  }
}

export function LanguageProvider({
  initialLocale = DEFAULT_LOCALE,
  children,
}: {
  initialLocale?: LocaleCode;
  children: React.ReactNode;
}) {
  const [locale, setLocaleState] = useState<LocaleCode>(initialLocale);

  const setLocale = useCallback((next: LocaleCode) => {
    setLocaleState(next);
    persistLocale(next);
    // Keep the document language in sync for screen readers and for the
    // browser's own translation / font-selection heuristics.
    document.documentElement.lang = next;
  }, []);

  const value = useMemo<LanguageContextValue>(
    () => ({
      locale,
      meta: LOCALES[locale],
      setLocale,
      t: (key: TranslationKey) => translate(locale, key),
    }),
    [locale, setLocale],
  );

  return (
    <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>
  );
}

export function useLanguage(): LanguageContextValue {
  const ctx = useContext(LanguageContext);
  if (!ctx) {
    throw new Error("useLanguage must be used inside a <LanguageProvider>");
  }
  return ctx;
}

/** Convenience hook for components that only need the translate function. */
export function useT(): (key: TranslationKey) => string {
  return useLanguage().t;
}
