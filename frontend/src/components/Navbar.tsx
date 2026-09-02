"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Menu, X } from "lucide-react";
import { motion } from "framer-motion";
import { LanguageSwitcher } from "@/components/LanguageSwitcher";
import { useT } from "@/lib/i18n/LanguageProvider";
import type { TranslationKey } from "@/lib/i18n/translations";
import { useAuth } from "@/lib/auth/AuthProvider";
import { cn } from "@/lib/utils";

const NAV_ITEMS: { href: string; key: TranslationKey }[] = [
  { href: "/analyze", key: "nav.analyze" },
  { href: "/toolkit", key: "nav.toolkit" },
  { href: "/lawyers", key: "nav.lawyers" },
  { href: "/cases", key: "nav.cases" },
  { href: "/knowledge", key: "nav.knowledge" },
  { href: "/messages", key: "nav.messages" },
  { href: "/about", key: "nav.about" },
];

export function Navbar() {
  const pathname = usePathname();
  const t = useT();
  const { user, ready, signOut } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", handleScroll);
    handleScroll();
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  // Close the drawer on navigation — otherwise it stays open over the new page.
  useEffect(() => {
    setMenuOpen(false);
  }, [pathname]);

  // Escape closes it, and the page behind must not scroll while it is open.
  useEffect(() => {
    if (!menuOpen) return;

    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") setMenuOpen(false);
    };
    document.addEventListener("keydown", onKeyDown);

    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";

    return () => {
      document.removeEventListener("keydown", onKeyDown);
      document.body.style.overflow = previousOverflow;
    };
  }, [menuOpen]);

  return (
    // `viewTransitionName` lifts the navbar out of the page snapshot during a
    // route change, so the content transitions underneath it while it stays
    // put. See the view-transition rules in globals.css.
    <nav
      style={{ viewTransitionName: "site-header" }}
      className={cn(
        "w-full sticky top-0 z-50 transition-all duration-300",
        scrolled 
          ? "bg-white/80 backdrop-blur-2xl border-b border-gray-200 shadow-sm" 
          : "bg-white/50 backdrop-blur-md border-b border-transparent"
      )}
    >
      <div className="px-4 sm:px-6 py-4 flex items-center justify-between gap-3 max-w-7xl mx-auto">
        {/* Left: Logo */}
        <Link href="/" className="flex items-center gap-3 group shrink-0">
          <div className="relative flex items-center justify-center w-10 h-10 rounded-xl overflow-hidden shadow-sm group-hover:shadow-md group-hover:scale-105 transition-all duration-300 border border-gray-100">
            <img src="/logo.png" alt="Nyaysetu Logo" className="w-full h-full object-cover" />
          </div>
          <span className="text-xl tracking-tight flex items-center font-serif">
            <span className="font-bold text-slate-900">Nyay</span>
            <span className="font-medium text-amber-600">setu</span>
          </span>
        </Link>

        {/* Center: Links (desktop) */}
        <div className="hidden md:flex items-center gap-6 lg:gap-8">
          {NAV_ITEMS.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              aria-current={pathname === item.href ? "page" : undefined}
              className={cn(
                "relative text-sm font-medium transition-colors whitespace-nowrap py-2",
                pathname === item.href
                  ? "text-slate-900"
                  : "text-gray-600 hover:text-slate-900",
              )}
            >
              {t(item.key)}
              {pathname === item.href && (
                <motion.div
                  layoutId="navbar-active-underline"
                  className="absolute bottom-0 left-0 right-0 h-0.5 bg-amber-500 rounded-full"
                  transition={{ type: "spring", stiffness: 380, damping: 30 }}
                />
              )}
            </Link>
          ))}
        </div>

        {/* Right: Language + Auth (desktop).
            `ready` gates this so a signed-in user never sees "Login" flash
            while localStorage is being read. */}
        <div className="hidden md:flex items-center gap-4 shrink-0">
          <LanguageSwitcher />
          {!ready ? (
            <div className="h-10 w-32 rounded-full bg-gray-100 animate-pulse" />
          ) : user ? (
            <>
              <Link
                href="/cases"
                className="flex items-center gap-2 text-sm font-medium text-gray-700 hover:text-black"
              >
                <span className="flex h-8 w-8 items-center justify-center rounded-full bg-amber-100 text-xs font-bold text-amber-800">
                  {user.name.charAt(0).toUpperCase()}
                </span>
                <span className="max-w-[120px] truncate">{user.name}</span>
              </Link>
              <button
                type="button"
                onClick={signOut}
                className="text-sm text-gray-600 hover:text-black font-medium whitespace-nowrap"
              >
                {t("nav.signOut")}
              </button>
            </>
          ) : (
            <>
              <Link
                href="/login"
                className="text-sm text-gray-600 hover:text-black font-medium whitespace-nowrap"
              >
                {t("nav.login")}
              </Link>
              <Link
                href="/register"
                className="bg-black text-white px-5 py-2.5 rounded-full text-sm font-medium hover:bg-gray-800 shadow-sm transition-all active:scale-[0.97] whitespace-nowrap"
              >
                {t("nav.register")}
              </Link>
            </>
          )}
        </div>

        {/* Right: language + menu trigger (mobile).
            The switcher stays outside the drawer: someone who cannot read the
            English menu needs to reach it without opening an English menu. */}
        <div className="flex md:hidden items-center gap-2">
          <LanguageSwitcher />
          <button
            type="button"
            onClick={() => setMenuOpen((open) => !open)}
            aria-expanded={menuOpen}
            aria-controls="mobile-nav"
            aria-label={menuOpen ? t("nav.closeMenu") : t("nav.openMenu")}
            className="flex h-10 w-10 items-center justify-center rounded-xl border border-gray-200 text-gray-700 transition-colors hover:bg-gray-50"
          >
            {menuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>
      </div>

      {/* Mobile drawer */}
      {menuOpen && (
        <>
          <button
            type="button"
            aria-hidden="true"
            tabIndex={-1}
            onClick={() => setMenuOpen(false)}
            className="fixed inset-0 top-[73px] z-40 bg-slate-900/20 backdrop-blur-sm md:hidden"
          />
          <motion.div
            id="mobile-nav"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ type: "spring", stiffness: 400, damping: 30 }}
            className="absolute inset-x-0 top-full z-50 border-b border-gray-100 bg-white shadow-lg md:hidden"
          >
            <div className="flex flex-col px-4 py-3">
              {NAV_ITEMS.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  aria-current={pathname === item.href ? "page" : undefined}
                  className={cn(
                    "rounded-lg px-3 py-3 text-base font-medium transition-colors",
                    pathname === item.href
                      ? "bg-amber-50 text-amber-900"
                      : "text-gray-700 hover:bg-gray-50",
                  )}
                >
                  {t(item.key)}
                </Link>
              ))}

              <div className="mt-3 flex flex-col gap-2 border-t border-gray-100 pt-3">
                {user ? (
                  <>
                    <div className="flex items-center gap-2.5 px-3 py-2">
                      <span className="flex h-9 w-9 items-center justify-center rounded-full bg-amber-100 text-sm font-bold text-amber-800">
                        {user.name.charAt(0).toUpperCase()}
                      </span>
                      <span className="truncate text-base font-medium text-gray-900">
                        {user.name}
                      </span>
                    </div>
                    <button
                      type="button"
                      onClick={signOut}
                      className="rounded-lg px-3 py-3 text-left text-base font-medium text-gray-700 transition-colors hover:bg-gray-50"
                    >
                      {t("nav.signOut")}
                    </button>
                  </>
                ) : (
                  <>
                    <Link
                      href="/login"
                      className="rounded-lg px-3 py-3 text-base font-medium text-gray-700 transition-colors hover:bg-gray-50"
                    >
                      {t("nav.login")}
                    </Link>
                    <Link
                      href="/register"
                      className="rounded-full bg-black px-5 py-3 text-center text-base font-medium text-white transition-all active:scale-[0.97] hover:bg-gray-800"
                    >
                      {t("nav.register")}
                    </Link>
                  </>
                )}
              </div>
            </div>
          </motion.div>
        </>
      )}
    </nav>
  );
}
