"use client";

/**
 * Global language picker.
 *
 * Options are labelled in their own script (हिन्दी, தமிழ், …) rather than in
 * English, so a user who can't read English can still find their language.
 */

import { useEffect, useRef, useState } from "react";
import { Check, Globe } from "lucide-react";
import { cn } from "@/lib/utils";
import { useLanguage } from "@/lib/i18n/LanguageProvider";
import { LOCALE_LIST } from "@/lib/i18n/locales";

export function LanguageSwitcher({ className }: { className?: string }) {
  const { locale, meta, setLocale, t } = useLanguage();
  const [open, setOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  // Close on outside click and on Escape.
  useEffect(() => {
    if (!open) return;

    const onPointerDown = (event: MouseEvent) => {
      if (!containerRef.current?.contains(event.target as Node)) setOpen(false);
    };
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") setOpen(false);
    };

    document.addEventListener("mousedown", onPointerDown);
    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.removeEventListener("mousedown", onPointerDown);
      document.removeEventListener("keydown", onKeyDown);
    };
  }, [open]);

  return (
    <div ref={containerRef} className={cn("relative", className)}>
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-haspopup="listbox"
        aria-expanded={open}
        aria-label={t("nav.chooseLanguage")}
        className="flex items-center gap-1.5 rounded-full border border-gray-200 px-3 py-1.5 text-sm font-medium text-gray-700 transition-colors hover:border-gray-300 hover:bg-gray-50"
      >
        <Globe className="h-4 w-4 text-gray-500" />
        <span>{meta.native}</span>
      </button>

      {open && (
        <ul
          role="listbox"
          aria-label={t("nav.chooseLanguage")}
          className="absolute right-0 z-50 mt-2 w-52 overflow-hidden rounded-xl border border-gray-100 bg-white py-1 shadow-lg"
        >
          {LOCALE_LIST.map((item) => {
            const active = item.code === locale;
            return (
              <li key={item.code}>
                <button
                  type="button"
                  role="option"
                  aria-selected={active}
                  lang={item.code}
                  onClick={() => {
                    setLocale(item.code);
                    setOpen(false);
                  }}
                  className={cn(
                    "flex w-full items-center justify-between gap-2 px-3 py-2 text-left text-sm transition-colors",
                    active ? "bg-amber-50 text-amber-900" : "text-gray-700 hover:bg-gray-50",
                  )}
                >
                  <span className="flex flex-col leading-tight">
                    <span className="font-medium">{item.native}</span>
                    {item.native !== item.label && (
                      <span className="text-[11px] text-gray-400">{item.label}</span>
                    )}
                  </span>
                  {active && <Check className="h-4 w-4 shrink-0 text-amber-600" />}
                </button>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
