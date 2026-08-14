"use client";

/**
 * Client-side session state.
 *
 * Until now the token was written to localStorage by the login page and read
 * ad hoc by whichever page needed it, so nothing else in the app knew whether
 * anyone was signed in — the navbar offered "Login" to users who already were.
 * This centralises it.
 *
 * The token is a JWT issued by the backend and every protected call sends it
 * as a bearer header. Storage is localStorage rather than an httpOnly cookie,
 * which is the weaker choice against XSS; switching to httpOnly cookies is
 * worth doing before real user data is on the line.
 */

import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

export interface SessionUser {
  id: number;
  name: string;
  role: "client" | "lawyer";
}

interface AuthContextValue {
  user: SessionUser | null;
  token: string | null;
  /** False until localStorage has been read, so the UI can avoid flicker. */
  ready: boolean;
  signIn: (token: string, user: SessionUser) => void;
  signOut: () => void;
  /** Authorization header for fetch, or an empty object when signed out. */
  authHeader: () => Record<string, string>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

const TOKEN_KEY = "token";
const USER_KEY = "nyaysetu_user";

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<SessionUser | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [ready, setReady] = useState(false);

  // localStorage is not available during server rendering, so the session is
  // resolved after mount. `ready` lets consumers render a neutral state until
  // then rather than flashing "Login" at a signed-in user.
  useEffect(() => {
    try {
      const storedToken = localStorage.getItem(TOKEN_KEY);
      const storedUser = localStorage.getItem(USER_KEY);
      if (storedToken) setToken(storedToken);
      if (storedUser) setUser(JSON.parse(storedUser) as SessionUser);
    } catch {
      // Corrupt or unavailable storage — treat as signed out.
    }
    setReady(true);
  }, []);

  // Keep tabs in sync: signing out in one should sign out the others.
  useEffect(() => {
    const onStorage = (event: StorageEvent) => {
      if (event.key !== TOKEN_KEY && event.key !== USER_KEY) return;
      const storedToken = localStorage.getItem(TOKEN_KEY);
      const storedUser = localStorage.getItem(USER_KEY);
      setToken(storedToken);
      setUser(storedUser ? (JSON.parse(storedUser) as SessionUser) : null);
    };
    window.addEventListener("storage", onStorage);
    return () => window.removeEventListener("storage", onStorage);
  }, []);

  const signIn = useCallback((nextToken: string, nextUser: SessionUser) => {
    localStorage.setItem(TOKEN_KEY, nextToken);
    localStorage.setItem(USER_KEY, JSON.stringify(nextUser));
    setToken(nextToken);
    setUser(nextUser);
  }, []);

  const signOut = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    setToken(null);
    setUser(null);
  }, []);

  const authHeader = useCallback(
    (): Record<string, string> => (token ? { Authorization: `Bearer ${token}` } : {}),
    [token],
  );

  const value = useMemo<AuthContextValue>(
    () => ({ user, token, ready, signIn, signOut, authHeader }),
    [user, token, ready, signIn, signOut, authHeader],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside an <AuthProvider>");
  return ctx;
}
