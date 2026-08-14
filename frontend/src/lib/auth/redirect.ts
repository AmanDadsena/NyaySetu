/**
 * Where to send someone once they are signed in.
 *
 * The gate on a protected route records what the user was reaching for, so
 * signing in should return them to it rather than to a dashboard they then
 * have to navigate out of.
 *
 * Only same-site paths are honoured. `next` arrives from the URL, so anyone
 * can put anything in it; accepting an absolute URL here would turn the login
 * page into an open redirect — a phishing link that genuinely begins with this
 * site's domain and lands somewhere else. A leading `//` is rejected for the
 * same reason, since browsers read it as protocol-relative.
 */
export function destinationAfterLogin(fallback = "/cases"): string {
  if (typeof window === "undefined") return fallback;
  const next = new URLSearchParams(window.location.search).get("next");
  if (next && next.startsWith("/") && !next.startsWith("//")) return next;
  return fallback;
}

/** Carry the pending destination across the login ↔ register links. */
export function withNext(path: string): string {
  if (typeof window === "undefined") return path;
  const next = new URLSearchParams(window.location.search).get("next");
  return next ? `${path}?next=${encodeURIComponent(next)}` : path;
}
