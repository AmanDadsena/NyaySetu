"use client";

/**
 * Scroll-triggered reveal.
 *
 * The obvious implementation — render at `opacity: 0` and animate to 1 — has a
 * failure mode this app cannot afford: if the script never runs, or runs late,
 * or an observer is unavailable, the content stays invisible forever. A page
 * about how to claim free legal aid must not depend on an animation succeeding.
 *
 * So this fails open. The server renders the children plainly visible, and the
 * hiding only happens on the client, only when an observer is available, and
 * only for elements that are *below the fold at mount* — where hiding cannot be
 * seen. Anything already on screen is simply left alone. If any of that is not
 * true, the reader gets static content instead of no content.
 */

import {
  useEffect,
  useRef,
  useState,
  type ElementType,
  type ReactNode,
} from "react";
import { cn } from "@/lib/utils";

type Phase = "static" | "hidden" | "revealed";

export interface RevealProps {
  children: ReactNode;
  /** Seconds to wait after entering the viewport. Stagger siblings with this. */
  delay?: number;
  /** Direction the content travels in from. */
  from?: "below" | "left" | "right" | "scale";
  className?: string;
  /** Rendered element. Use a semantic tag rather than wrapping in a div. */
  as?: ElementType;
}

const OFFSET: Record<NonNullable<RevealProps["from"]>, string> = {
  below: "translate-y-8",
  left: "-translate-x-8",
  right: "translate-x-8",
  scale: "scale-95",
};

export function Reveal({
  children,
  delay = 0,
  from = "below",
  className,
  as: Tag = "div",
}: RevealProps) {
  const ref = useRef<HTMLElement>(null);
  const [phase, setPhase] = useState<Phase>("static");

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    // Someone who has asked for less motion gets the content, not the journey.
    const reduced =
      typeof window.matchMedia === "function" &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduced || typeof IntersectionObserver === "undefined") return;

    // Only take over elements the reader cannot currently see. Hiding something
    // already on screen would be a visible flicker, and revealing something
    // already read is pointless.
    const box = el.getBoundingClientRect();
    if (box.top < window.innerHeight * 0.9) return;

    setPhase("hidden");

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (!entry.isIntersecting) return;
        setPhase("revealed");
        observer.disconnect();
      },
      // Fire a little before the element's edge so the motion finishes about
      // when it reaches comfortable reading position.
      { rootMargin: "0px 0px -10% 0px", threshold: 0.05 },
    );

    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  return (
    <Tag
      ref={ref}
      className={cn(
        phase !== "static" &&
          "transition-[opacity,transform] duration-700 ease-[cubic-bezier(0.22,1,0.36,1)] motion-reduce:transition-none",
        phase === "hidden" && cn("opacity-0", OFFSET[from]),
        phase === "revealed" && "opacity-100 translate-x-0 translate-y-0 scale-100",
        className,
      )}
      style={phase === "revealed" && delay ? { transitionDelay: `${delay}s` } : undefined}
    >
      {children}
    </Tag>
  );
}
