"use client";

/**
 * Sign-in prompt attached to actions rather than to routes.
 *
 * Gating whole pages taught people nothing about what they were signing up
 * for — a person who clicked "Toolkit" landed on a login form having never
 * seen the thing they were meant to want an account for. So every page stays
 * open and browsable: the tabs, the dropdowns, the templates, the lawyer
 * directory. The prompt arrives only when someone actually presses the button
 * that does the work, at which point the value of an account is obvious
 * because they are two clicks from the answer.
 *
 * Pressing that button sends them to the sign-in page, carrying `next` so that
 * signing in returns them to the tool they were using rather than dropping
 * them on a dashboard they then have to navigate out of. The reason they were
 * stopped travels in sessionStorage rather than the URL — it is presentational
 * text, and query strings get copied, shared and logged.
 *
 * This is a product boundary, not a security one. The toolkit endpoints are
 * public and this code runs in the browser, so anyone who wants the JSON can
 * have it. Anything that must actually be protected is protected by the bearer
 * token the API checks on every request.
 */

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
} from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "./AuthProvider";

/** Where the reason for the prompt is parked across the navigation. */
export const AUTH_REASON_KEY = "nyaysetu_auth_reason";

type PendingAction = () => void | Promise<void>;

interface AuthGateValue {
  /**
   * Run `action` if signed in; otherwise send the user to the sign-in page.
   * `reason` is shown there and should say what they were trying to do, in
   * their words.
   */
  requireAuth: (action: PendingAction, reason?: string) => void;
  signedIn: boolean;
}

const AuthGateContext = createContext<AuthGateValue | null>(null);

export function AuthGateProvider({ children }: { children: React.ReactNode }) {
  const { token, user, ready } = useAuth();
  const router = useRouter();

  // A click that lands before localStorage has been read cannot be decided
  // yet: `signedIn` is false at that point for signed-in and signed-out users
  // alike, so acting on it would bounce a logged-in user to the login page.
  // The click is held here and resolved by the effect below once `ready`.
  const deferred = useRef<{ action: PendingAction; reason?: string } | null>(null);

  const signedIn = ready && !!token && !!user;

  const sendToLogin = useCallback(
    (reason?: string) => {
      try {
        sessionStorage.setItem(AUTH_REASON_KEY, reason ?? "");
      } catch {
        // Private mode or storage disabled — the prompt simply loses its
        // subtitle, which is cosmetic.
      }
      const next = window.location.pathname + window.location.search;
      router.push(`/login?next=${encodeURIComponent(next)}`);
    },
    [router],
  );

  const requireAuth = useCallback(
    (action: PendingAction, reason?: string) => {
      if (!ready) {
        deferred.current = { action, reason };
        return;
      }
      if (signedIn) {
        void action();
        return;
      }
      sendToLogin(reason);
    },
    [ready, signedIn, sendToLogin],
  );

  useEffect(() => {
    if (!ready || !deferred.current) return;
    const { action, reason } = deferred.current;
    deferred.current = null;
    if (signedIn) void action();
    else sendToLogin(reason);
  }, [ready, signedIn, sendToLogin]);

  const value = useMemo<AuthGateValue>(
    () => ({ requireAuth, signedIn }),
    [requireAuth, signedIn],
  );

  return (
    <AuthGateContext.Provider value={value}>{children}</AuthGateContext.Provider>
  );
}

export function useAuthGate(): AuthGateValue {
  const ctx = useContext(AuthGateContext);
  if (!ctx) throw new Error("useAuthGate must be used inside an <AuthGateProvider>");
  return ctx;
}
