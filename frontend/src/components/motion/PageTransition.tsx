"use client";

/**
 * Page-level view transitions.
 *
 * Keyed on the pathname so every navigation is a real unmount/mount pair, which
 * is what makes React fire `exit` on the outgoing page and `enter` on the
 * incoming one. Without the key the wrapper would persist across navigation and
 * React would see an update rather than a swap.
 *
 * The `enter`/`exit` maps route each navigation to a CSS class by transition
 * type: links tagged `nav-forward` or `nav-back` (via `<Link transitionTypes>`)
 * slide in the matching direction, and everything else gets the plain crossfade.
 * `default="none"` keeps this wrapper out of transitions it has no part in.
 *
 * The animations themselves live in globals.css under VIEW TRANSITIONS.
 */

import { ViewTransition } from "react";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";

export function PageTransition({ children }: { children: ReactNode }) {
  const pathname = usePathname();

  return (
    <ViewTransition
      key={pathname}
      enter={{
        "nav-forward": "nav-forward",
        "nav-back": "nav-back",
        default: "page-enter",
      }}
      exit={{
        "nav-forward": "nav-forward",
        "nav-back": "nav-back",
        default: "page-exit",
      }}
      default="none"
    >
      {children}
    </ViewTransition>
  );
}
