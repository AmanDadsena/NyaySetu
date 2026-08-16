"use client";

/**
 * A number that counts up when it scrolls into view.
 *
 * Same contract as `Reveal`: the final value is what the server renders, so a
 * reader who never runs the animation still reads the real figure. The count is
 * an embellishment layered on top of a correct static number, never the only
 * way to arrive at it.
 *
 * Every figure this animates is a measured one — see `lib/site-stats.ts`. A
 * counter spinning up to an invented total is the single most dishonest thing
 * a landing page can do, so the component is deliberately not capable of it:
 * it takes a number someone can check, and only makes it arrive with emphasis.
 */

import { useEffect, useRef, useState } from "react";

export interface CountUpProps {
  value: number;
  decimals?: number;
  prefix?: string;
  suffix?: string;
  /** Milliseconds for the full count. */
  duration?: number;
  className?: string;
}

/** Fast out of the gate, gentle at rest — the number settles rather than stops. */
const easeOutExpo = (t: number) => (t === 1 ? 1 : 1 - Math.pow(2, -10 * t));

export function CountUp({
  value,
  decimals = 0,
  prefix = "",
  suffix = "",
  duration = 1400,
  className,
}: CountUpProps) {
  const ref = useRef<HTMLSpanElement>(null);
  const [shown, setShown] = useState(value);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    const reduced =
      typeof window.matchMedia === "function" &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduced || typeof IntersectionObserver === "undefined") return;

    // Only animate a figure the reader has not already read.
    if (el.getBoundingClientRect().top < window.innerHeight * 0.9) return;

    setShown(0);

    let frame = 0;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (!entry.isIntersecting) return;
        observer.disconnect();

        const start = performance.now();
        const tick = (now: number) => {
          const progress = Math.min((now - start) / duration, 1);
          setShown(value * easeOutExpo(progress));
          if (progress < 1) frame = requestAnimationFrame(tick);
        };
        frame = requestAnimationFrame(tick);
      },
      { threshold: 0.2 },
    );

    observer.observe(el);
    return () => {
      observer.disconnect();
      cancelAnimationFrame(frame);
    };
  }, [value, duration]);

  const text = shown.toLocaleString("en-IN", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });

  return (
    <span ref={ref} className={className}>
      {/* Tabular figures stop the width jittering as digits change. */}
      <span className="tabular-nums">
        {prefix}
        {text}
      </span>
      {suffix}
    </span>
  );
}
