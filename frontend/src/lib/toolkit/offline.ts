/**
 * The deadline calculator, running in the browser.
 *
 * The toolkit's maths is a lookup table plus calendar arithmetic — nothing that
 * needs a server. Requiring one meant that a person on a patchy connection, or
 * none, got nothing from a tool that could have answered instantly. So the
 * tables are fetched once, cached, and the arithmetic repeated here.
 *
 * This is a deliberate duplication of `backend/app/tools/limitation.py`, and
 * duplicated logic drifts. `backend/scripts/check_offline_parity.py` runs every
 * rule through both implementations across a spread of dates and fails the
 * build if they ever disagree, so the copy cannot rot quietly.
 *
 * Dates are handled in UTC throughout. A limitation period is a count of
 * calendar days, not an instant, and constructing local-time Dates makes the
 * answer depend on the reader's timezone — which for a filing deadline is the
 * difference between in time and out of time.
 */

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const CACHE_KEY = "nyaysetu_toolkit_bundle";
/** Must match `SCHEMA_VERSION` in `backend/app/tools/bundle.py`. */
const SCHEMA = 1;

export interface LimitationRuleData {
  id: string;
  label: string;
  category: string;
  trigger: string;
  citation: string;
  years: number | null;
  months: number | null;
  days: number | null;
  condonable: boolean;
  condonation_note: string;
  notes: string[];
  related: string[];
}

export interface ToolkitBundle {
  schema: number;
  generated: string;
  limitation: LimitationRuleData[];
  forum: unknown;
  fees: unknown;
  holidays: {
    fixed: Record<string, string>;
    notified: Record<string, string[]>;
  };
}

export interface LocalLimitationResult {
  rule_id: string;
  label: string;
  trigger: string;
  citation: string;
  has_limitation: boolean;
  start_date: string;
  deadline: string | null;
  days_remaining: number | null;
  expired: boolean;
  days_overdue: number | null;
  urgency: "none" | "urgent" | "soon" | "comfortable" | "expired";
  condonable: boolean;
  condonation_note: string;
  notes: string[];
  filing_date: string | null;
  filing_date_confidence: string;
  filing_reasons: string[];
  /** True when this came from the cache rather than the server. */
  offline: boolean;
}

// ── Cache ───────────────────────────────────────────────────────────────

export function readCachedBundle(): ToolkitBundle | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = localStorage.getItem(CACHE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as ToolkitBundle;
    // A payload whose shape has moved on is worse than none: it would be read
    // with fields that no longer mean what this code thinks they mean.
    if (parsed.schema !== SCHEMA) {
      localStorage.removeItem(CACHE_KEY);
      return null;
    }
    return parsed;
  } catch {
    return null;
  }
}

/**
 * Fetch the tables and cache them. Returns whatever is already cached if the
 * network fails, so calling this on every visit is safe when offline.
 */
export async function refreshBundle(): Promise<ToolkitBundle | null> {
  try {
    const res = await fetch(`${API}/api/tools/bundle`);
    if (!res.ok) throw new Error(String(res.status));
    const data = (await res.json()) as ToolkitBundle;
    if (data.schema === SCHEMA) {
      try {
        localStorage.setItem(CACHE_KEY, JSON.stringify(data));
      } catch {
        // Storage full or blocked — the tables still work for this session.
      }
    }
    return data;
  } catch {
    return readCachedBundle();
  }
}

// ── Date helpers, all UTC ───────────────────────────────────────────────

function parseISO(iso: string): Date {
  const [y, m, d] = iso.split("-").map(Number);
  return new Date(Date.UTC(y, m - 1, d));
}

function toISO(d: Date): string {
  return d.toISOString().slice(0, 10);
}

function addDays(d: Date, n: number): Date {
  return new Date(d.getTime() + n * 86_400_000);
}

function daysBetween(a: Date, b: Date): number {
  return Math.round((a.getTime() - b.getTime()) / 86_400_000);
}

/**
 * Add a period in calendar terms, matching `_add_period` on the server.
 *
 * Three years from 29 February 2024 is 28 February 2027, and one month from 31
 * January is 28 February — so the day is clamped down to the last valid one of
 * the target month rather than spilling into the next.
 */
function addPeriod(start: Date, rule: LimitationRuleData): Date {
  let year = start.getUTCFullYear();
  let month = start.getUTCMonth(); // 0-based
  const day = start.getUTCDate();

  if (rule.years) year += rule.years;
  if (rule.months) {
    const total = month + rule.months;
    year += Math.floor(total / 12);
    month = ((total % 12) + 12) % 12;
  }

  if (rule.years || rule.months) {
    // Last day of the target month, so 31 -> 28/29/30 as required.
    const lastDay = new Date(Date.UTC(year, month + 1, 0)).getUTCDate();
    let shifted = new Date(Date.UTC(year, month, Math.min(day, lastDay)));
    if (rule.days) shifted = addDays(shifted, rule.days);
    return shifted;
  }

  return addDays(start, rule.days ?? 0);
}

// ── Working days, matching holidays.py ──────────────────────────────────

function isWeekend(d: Date): boolean {
  const wd = d.getUTCDay(); // 0 Sun … 6 Sat
  return wd === 0 || wd === 6;
}

function holidayName(d: Date, bundle: ToolkitBundle): string | null {
  const year = String(d.getUTCFullYear());
  if ((bundle.holidays.notified[year] ?? []).includes(toISO(d))) {
    return "Court holiday (notified)";
  }
  const key = toISO(d).slice(5); // MM-DD
  return bundle.holidays.fixed[key] ?? null;
}

function isWorkingDay(d: Date, bundle: ToolkitBundle): boolean {
  return !isWeekend(d) && holidayName(d, bundle) === null;
}

const WEEKDAYS = [
  "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday",
];

/**
 * Section 4: a deadline falling on a day the court is shut moves to the next
 * day it is open. Never moves earlier, and reports every day it skipped.
 */
function resolveFilingDate(
  deadline: Date,
  bundle: ToolkitBundle,
): { filing: Date; reasons: string[]; confidence: string } {
  if (isWorkingDay(deadline, bundle)) {
    return { filing: deadline, reasons: [], confidence: "high" };
  }

  const reasons: string[] = [];
  let cursor = deadline;
  for (let i = 0; i < 30; i++) {
    if (isWorkingDay(cursor, bundle)) break;
    reasons.push(
      isWeekend(cursor)
        ? `${toISO(cursor)} is a ${WEEKDAYS[cursor.getUTCDay()]}`
        : `${toISO(cursor)} is ${holidayName(cursor, bundle)}`,
    );
    cursor = addDays(cursor, 1);
  }

  const year = String(deadline.getUTCFullYear());
  const haveCalendar = (bundle.holidays.notified[year] ?? []).length > 0;
  return { filing: cursor, reasons, confidence: haveCalendar ? "high" : "partial" };
}

// ── The calculation ─────────────────────────────────────────────────────

export function calculateLocally(
  bundle: ToolkitBundle,
  ruleId: string,
  eventDateISO: string,
  todayISO?: string,
): LocalLimitationResult {
  const rule = bundle.limitation.find((r) => r.id === ruleId);
  if (!rule) throw new Error(`Unknown limitation rule: ${ruleId}`);

  const start = parseISO(eventDateISO);
  const today = todayISO ? parseISO(todayISO) : parseISO(toISO(new Date()));

  const base = {
    rule_id: rule.id,
    label: rule.label,
    trigger: rule.trigger,
    citation: rule.citation,
    start_date: eventDateISO,
    condonable: rule.condonable,
    condonation_note: rule.condonation_note,
    offline: true,
  };

  if (rule.years === null && rule.months === null && rule.days === null) {
    return {
      ...base,
      has_limitation: false,
      deadline: null,
      days_remaining: null,
      expired: false,
      days_overdue: null,
      urgency: "none",
      notes: [...rule.notes],
      filing_date: null,
      filing_date_confidence: "high",
      filing_reasons: [],
    };
  }

  const deadline = addPeriod(start, rule);
  const remaining = daysBetween(deadline, today);
  const expired = remaining < 0;

  const urgency: LocalLimitationResult["urgency"] = expired
    ? "expired"
    : remaining <= 7
      ? "urgent"
      : remaining <= 30
        ? "soon"
        : "comfortable";

  const { filing, reasons, confidence } = resolveFilingDate(deadline, bundle);

  return {
    ...base,
    has_limitation: true,
    deadline: toISO(deadline),
    days_remaining: expired ? 0 : Math.max(remaining, 0),
    expired,
    days_overdue: expired ? Math.abs(remaining) : null,
    urgency,
    notes: [
      ...rule.notes,
      "The day the period runs from is excluded, per Section 12(1) of the " +
        "Limitation Act, 1963.",
    ],
    filing_date: toISO(filing),
    filing_date_confidence: confidence,
    filing_reasons: reasons,
  };
}
