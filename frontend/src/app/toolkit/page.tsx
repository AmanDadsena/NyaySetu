"use client";

/**
 * Toolkit — the things people otherwise pay a lawyer to do for them.
 *
 * Deadline, forum, paperwork, and what it all costs. None of it calls a model:
 * the backend answers from lookup tables and calendar arithmetic, so results
 * are instant and identical every time. For something that tells a person
 * whether they still have the right to sue, that matters more than eloquence.
 */

import { useCallback, useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  CalendarClock,
  CheckCircle2,
  Clock,
  Copy,
  Download,
  FileText,
  Loader2,
  MapPin,
  Printer,
  Scale,
  CalendarDays,
  IndianRupee,
  BellRing,
  Share2,
  MessageCircle,
  BadgeIndianRupee,
  Scale as ScaleIcon,
  FileSearch,
  Landmark,
  Sparkles,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { TimelineTool } from "@/components/toolkit/TimelineTool";
import { FeesTool } from "@/components/toolkit/FeesTool";
import { TrackerTool } from "@/components/toolkit/TrackerTool";
import { useAuthGate } from "@/lib/auth/AuthGate";
import { useT } from "@/lib/i18n/LanguageProvider";
import { CitationsTool } from "@/components/toolkit/CitationsTool";
import { StampDutyTool } from "@/components/toolkit/StampDutyTool";
import { MaintenanceTool } from "@/components/toolkit/MaintenanceTool";
import { CasePlanTool } from "@/components/toolkit/CasePlanTool";
import { calculateLocally, readCachedBundle, refreshBundle } from "@/lib/toolkit/offline";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type Tab =
  | "plan"
  | "deadline"
  | "forum"
  | "draft"
  | "timeline"
  | "fees"
  | "tracker"
  | "stampduty"
  | "maintenance"
  | "citations";

const TABS: Tab[] = [
  "plan",
  "deadline",
  "forum",
  "draft",
  "timeline",
  "fees",
  "tracker",
  "stampduty",
  "maintenance",
  "citations",
];

// ── Shared types ───────────────────────────────────────────────────────
interface LimitationRule {
  id: string;
  label: string;
  category: string;
  trigger: string;
  citation: string;
  has_limitation: boolean;
}

interface LimitationResult {
  label: string;
  trigger: string;
  citation: string;
  has_limitation: boolean;
  deadline: string | null;
  days_remaining: number | null;
  expired: boolean;
  days_overdue: number | null;
  urgency: "none" | "urgent" | "soon" | "comfortable" | "expired";
  condonable: boolean;
  condonation_note: string;
  notes: string[];
  /** Last day the court is actually open, after Section 4. */
  filing_date: string | null;
  /** high where the court's notified calendar was consulted, partial otherwise. */
  filing_date_confidence: string;
  /** One entry per non-working day skipped, in the order they were skipped. */
  filing_reasons: string[];
}

/** Whether the deployment has a court's notified holiday list to work from. */
interface CalendarStatus {
  configured: boolean;
  notified_days_this_year: number;
  fixed_holidays: number;
}

interface ForumRule {
  id: string;
  label: string;
  category: string;
  value_question: string | null;
}

interface ForumResult {
  label: string;
  value_tier: string | null;
  forum: {
    name: string;
    where: string;
    fee: string;
    how_to_file: string;
    documents: string[];
    lawyer_needed: string;
    typical_duration: string;
    notes: string[];
  };
  limitation: { id: string; label: string; trigger: string }[];
}

interface TemplateField {
  name: string;
  label: string;
  kind: "text" | "textarea" | "date" | "number";
  required: boolean;
  placeholder: string;
  help: string;
}

interface DocTemplate {
  id: string;
  title: string;
  description: string;
  category: string;
  citation: string;
  fee: string;
  fields: TemplateField[];
  after: string[];
}

interface GeneratedDoc {
  title: string;
  body: string;
  citation: string;
  after: string[];
  missing: string[];
}

// ── Small pieces ───────────────────────────────────────────────────────
function SectionCard({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div className={cn("rounded-2xl border border-gray-200 bg-white p-5 sm:p-6", className)}>
      {children}
    </div>
  );
}

function Label({ children }: { children: React.ReactNode }) {
  return <span className="mb-1.5 block text-sm font-medium text-gray-700">{children}</span>;
}

const inputClass =
  "w-full rounded-xl border border-gray-200 px-3.5 py-2.5 text-sm transition-colors " +
  "focus:border-transparent focus:outline-none focus:ring-2 focus:ring-black";

/** Countdown, sized and coloured by how much trouble you are in. */
function DeadlineDial({ result }: { result: LimitationResult }) {
  if (!result.has_limitation) {
    return (
      <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-5">
        <div className="flex items-center gap-2 text-emerald-800">
          <CheckCircle2 className="h-5 w-5 shrink-0" />
          <span className="font-semibold">No limitation period applies</span>
        </div>
        <p className="mt-1.5 text-sm text-emerald-900/80">
          Your right to file is not time-barred. Evidence and witnesses still fade,
          so do not treat that as a reason to wait.
        </p>
      </div>
    );
  }

  const tone = {
    expired: { box: "border-red-200 bg-red-50", num: "text-red-700", label: "text-red-900/80" },
    urgent: { box: "border-red-200 bg-red-50", num: "text-red-700", label: "text-red-900/80" },
    soon: { box: "border-amber-200 bg-amber-50", num: "text-amber-700", label: "text-amber-900/80" },
    comfortable: {
      box: "border-emerald-200 bg-emerald-50",
      num: "text-emerald-700",
      label: "text-emerald-900/80",
    },
    none: { box: "border-gray-200 bg-gray-50", num: "text-gray-700", label: "text-gray-600" },
  }[result.urgency];

  return (
    <div className={cn("rounded-xl border p-5", tone.box)}>
      <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
        <span className={cn("text-4xl font-bold tabular-nums leading-none", tone.num)}>
          {result.expired ? result.days_overdue : result.days_remaining}
        </span>
        <span className={cn("text-sm font-medium", tone.label)}>
          {result.expired ? "days past the deadline" : "days left to file"}
        </span>
      </div>
      <p className={cn("mt-2 text-sm", tone.label)}>
        Deadline:{" "}
        <strong className="tabular-nums">
          {result.deadline
            ? new Date(result.deadline).toLocaleDateString("en-IN", {
                day: "numeric",
                month: "long",
                year: "numeric",
              })
            : "—"}
        </strong>
      </p>
      {result.expired && (
        <p className={cn("mt-2 text-sm", tone.label)}>
          {result.condonable
            ? "The period has run, but it can be extended. " + result.condonation_note
            : "This period cannot be extended. Speak to a lawyer about whether any other remedy remains open — free legal aid is available on 15100."}
        </p>
      )}
    </div>
  );
}

/**
 * Section 4 of the Limitation Act: where the period expires on a day the court
 * is closed, you may file on the next day it opens. That is a real extra day
 * or two, and people miss it.
 *
 * The panel shows the working day separately from the statutory deadline
 * rather than replacing it, and says which days were skipped. Where no
 * notified court calendar is configured the backend reports `partial` — only
 * weekends and fixed national holidays were checked — and that is stated
 * plainly, because a movable festival could still push the date later and
 * relying on the earlier date is the safe error.
 */
function FilingDayPanel({
  result,
  calendar,
}: {
  result: LimitationResult;
  calendar: CalendarStatus | null;
}) {
  if (!result.has_limitation || !result.filing_date || !result.deadline) return null;

  const moved = result.filing_date !== result.deadline;
  const partial = result.filing_date_confidence !== "high";

  return (
    <div className="mt-4 rounded-xl border border-gray-200 bg-white p-4">
      <h3 className="flex items-center gap-2 text-sm font-semibold text-gray-900">
        <Landmark className="h-4 w-4 shrink-0 text-gray-400" />
        Last day the court is open
      </h3>

      <div className="mt-3 grid gap-3 sm:grid-cols-2">
        <div className="rounded-lg bg-gray-50 px-3.5 py-2.5">
          <p className="text-xs font-semibold uppercase tracking-wider text-gray-400">
            Statutory deadline
          </p>
          <p className="mt-0.5 text-sm font-medium tabular-nums text-gray-700">
            {new Date(result.deadline).toLocaleDateString("en-IN", {
              weekday: "short",
              day: "numeric",
              month: "long",
              year: "numeric",
            })}
          </p>
        </div>
        <div
          className={cn(
            "rounded-lg px-3.5 py-2.5",
            moved ? "bg-emerald-50" : "bg-gray-50",
          )}
        >
          <p
            className={cn(
              "text-xs font-semibold uppercase tracking-wider",
              moved ? "text-emerald-600" : "text-gray-400",
            )}
          >
            You can file until
          </p>
          <p
            className={cn(
              "mt-0.5 text-sm font-medium tabular-nums",
              moved ? "text-emerald-900" : "text-gray-700",
            )}
          >
            {new Date(result.filing_date).toLocaleDateString("en-IN", {
              weekday: "short",
              day: "numeric",
              month: "long",
              year: "numeric",
            })}
          </p>
        </div>
      </div>

      <p className="mt-3 text-sm text-gray-600">
        {moved ? (
          <>
            The period expires on a day the court is closed, so Section 4 of the
            Limitation Act, 1963 lets you file on the next working day.
          </>
        ) : (
          <>
            The deadline falls on a working day, so Section 4 gives you nothing
            extra here.
          </>
        )}
      </p>

      {result.filing_reasons.length > 0 && (
        <ul className="mt-2 space-y-1">
          {result.filing_reasons.map((reason, i) => (
            <li key={i} className="flex gap-2 text-xs text-gray-500">
              <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-gray-300" />
              Skipped: {reason}
            </li>
          ))}
        </ul>
      )}

      {partial && (
        <p className="mt-2 flex items-start gap-1.5 text-xs text-amber-800">
          <AlertTriangle className="mt-0.5 h-3.5 w-3.5 shrink-0" />
          Only weekends and fixed national holidays were checked
          {calendar && !calendar.configured
            ? " — no notified court calendar is configured"
            : ""}
          . Movable festivals are not, because their dates shift and a wrong one
          would move a filing deadline. Treat this as the earliest safe date and
          confirm the court&rsquo;s calendar before relying on the extra days.
        </p>
      )}

      {!partial && calendar?.configured && (
        <p className="mt-2 text-xs text-gray-500">
          Checked against {calendar.notified_days_this_year} notified holidays for
          this year, plus weekends.
        </p>
      )}
    </div>
  );
}

// ── Page ───────────────────────────────────────────────────────────────
export default function ToolkitPage() {
  const { requireAuth } = useAuthGate();
  const t = useT();
  const [tab, setTab] = useState<Tab>("plan");
  /** Set when the last deadline came from the cached tables, not the server. */
  const [computedOffline, setComputedOffline] = useState(false);
  /** Pre-selected situation, when the analyser sent the user here. */
  const [planSituation, setPlanSituation] = useState("");
  const [shared, setShared] = useState(false);

  // Deadline
  const [limRules, setLimRules] = useState<LimitationRule[]>([]);
  const [limId, setLimId] = useState("");
  const [limDate, setLimDate] = useState("");
  const [limResult, setLimResult] = useState<LimitationResult | null>(null);
  const [calendar, setCalendar] = useState<CalendarStatus | null>(null);

  // Forum
  const [forumRules, setForumRules] = useState<ForumRule[]>([]);
  const [forumId, setForumId] = useState("");
  const [claimValue, setClaimValue] = useState("");
  const [forumResult, setForumResult] = useState<ForumResult | null>(null);

  // Draft
  const [templates, setTemplates] = useState<DocTemplate[]>([]);
  const [templateId, setTemplateId] = useState("");
  const [formData, setFormData] = useState<Record<string, string>>({});
  const [doc, setDoc] = useState<GeneratedDoc | null>(null);

  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  // Restore whatever was encoded in the link. A lawyer sends a client a URL
  // and it opens on the right tab with the right selection already made —
  // no account, no explaining which dropdown to touch.
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const t = params.get("t") as Tab | null;
    if (t && TABS.includes(t)) setTab(t);
    if (params.get("rule")) setLimId(params.get("rule")!);
    if (params.get("on")) setLimDate(params.get("on")!);
    if (params.get("problem")) setForumId(params.get("problem")!);
    if (params.get("value")) setClaimValue(params.get("value")!);
    // Sent by the document analyser, which knows the template and the
    // situation before the user has touched anything.
    if (params.get("template")) setTemplateId(params.get("template")!);
    if (params.get("situation")) setPlanSituation(params.get("situation")!);
  }, []);

  // Warm the offline tables while the connection is good, so the deadline
  // calculator still answers when it is not. Cheap, cached, and it fails
  // silently — nothing here is worth interrupting the page for.
  useEffect(() => {
    void refreshBundle();
  }, []);

  useEffect(() => {
    Promise.all([
      fetch(`${API}/api/tools/limitation`).then((r) => r.json()),
      fetch(`${API}/api/tools/forum`).then((r) => r.json()),
      fetch(`${API}/api/tools/documents`).then((r) => r.json()),
      fetch(`${API}/api/tools/calendar`).then((r) => r.json()),
    ])
      .then(([lim, fo, docs, cal]) => {
        setLimRules(lim.rules ?? []);
        setForumRules(fo.rules ?? []);
        setTemplates(docs.templates ?? []);
        setCalendar(cal ?? null);
      })
      .catch(() => setError("Could not reach the server. Is the backend running?"));
  }, []);

  const post = useCallback(async (path: string, body: unknown) => {
    setBusy(true);
    setError(null);
    try {
      const res = await fetch(`${API}${path}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const json = await res.json();
      if (!res.ok) throw new Error(json.detail || "Request failed");
      return json;
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong");
      return null;
    } finally {
      setBusy(false);
    }
  }, []);

  const activeTemplate = useMemo(
    () => templates.find((t) => t.id === templateId) ?? null,
    [templates, templateId],
  );

  const selectedLimRule = useMemo(
    () => limRules.find((r) => r.id === limId) ?? null,
    [limRules, limId],
  );

  const selectedForumRule = useMemo(
    () => forumRules.find((r) => r.id === forumId) ?? null,
    [forumRules, forumId],
  );

  const grouped = <T extends { category: string }>(items: T[]) => {
    const map = new Map<string, T[]>();
    for (const item of items) {
      const list = map.get(item.category) ?? [];
      list.push(item);
      map.set(item.category, list);
    }
    return [...map.entries()];
  };

  /** Encode the current selection so the link reproduces this screen. */
  const shareLink = async () => {
    const params = new URLSearchParams({ t: tab });
    if (tab === "deadline") {
      if (limId) params.set("rule", limId);
      if (limDate) params.set("on", limDate);
    } else if (tab === "forum") {
      if (forumId) params.set("problem", forumId);
      if (claimValue) params.set("value", claimValue);
    }
    const url = `${window.location.origin}${window.location.pathname}?${params}`;
    window.history.replaceState(null, "", url);
    await navigator.clipboard.writeText(url);
    setShared(true);
    setTimeout(() => setShared(false), 2000);
  };

  /**
   * WhatsApp is how this actually reaches people in India. Its formatting is
   * not Markdown — *single* asterisks bold, and monospace blocks survive
   * badly — so the text is rewritten rather than pasted verbatim.
   */
  const shareOnWhatsApp = () => {
    const NL = String.fromCharCode(10);
    let text = "";

    if (tab === "deadline" && limResult) {
      const head = "*" + limResult.label + "*";
      const body = !limResult.has_limitation
        ? "No limitation period applies."
        : limResult.expired
          ? "Deadline passed " + limResult.days_overdue + " days ago (" + limResult.deadline + ")."
          : limResult.days_remaining + " days left. Deadline: " + limResult.deadline + ".";
      text = [head, body, "_" + limResult.citation + "_"].join(NL + NL);
    } else if (tab === "forum" && forumResult) {
      const f = forumResult.forum;
      text = [
        "*" + f.name + "*",
        "*Where:* " + f.where,
        "*Fee:* " + f.fee,
        "*Lawyer needed:* " + f.lawyer_needed,
        "*Documents:*" + NL + f.documents.map((d) => "\u2022 " + d).join(NL),
      ].join(NL + NL);
    } else if (tab === "draft" && doc) {
      // WhatsApp bolds with single asterisks, not double.
      text = doc.body.replace(/\*\*/g, "*");
    }

    if (!text) return;
    text += NL + NL + "via Nyaysetu \u2014 " + window.location.origin;
    window.open("https://wa.me/?text=" + encodeURIComponent(text), "_blank", "noopener");
  };

  const canShareResult =
    (tab === "deadline" && !!limResult) ||
    (tab === "forum" && !!forumResult) ||
    (tab === "draft" && !!doc);

  const copyDoc = async () => {
    if (!doc) return;
    await navigator.clipboard.writeText(doc.body);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const downloadDoc = () => {
    if (!doc) return;
    const blob = new Blob([doc.body], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${doc.title.toLowerCase().replace(/\s+/g, "-")}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const tabs: { id: Tab; label: string; icon: typeof Clock; blurb: string }[] = [
    { id: "plan", label: t("toolkit.tab.plan"), icon: Sparkles, blurb: t("toolkit.blurb.plan") },
    { id: "deadline", label: t("toolkit.tab.deadline"), icon: CalendarClock, blurb: t("toolkit.blurb.deadline") },
    { id: "forum", label: t("toolkit.tab.forum"), icon: MapPin, blurb: t("toolkit.blurb.forum") },
    { id: "draft", label: t("toolkit.tab.draft"), icon: FileText, blurb: t("toolkit.blurb.draft") },
    { id: "timeline", label: t("toolkit.tab.timeline"), icon: CalendarDays, blurb: t("toolkit.blurb.timeline") },
    { id: "fees", label: t("toolkit.tab.fees"), icon: IndianRupee, blurb: t("toolkit.blurb.fees") },
    { id: "tracker", label: t("toolkit.tab.tracker"), icon: BellRing, blurb: t("toolkit.blurb.tracker") },
    { id: "stampduty", label: t("toolkit.tab.stampduty"), icon: BadgeIndianRupee, blurb: t("toolkit.blurb.stampduty") },
    { id: "maintenance", label: t("toolkit.tab.maintenance"), icon: ScaleIcon, blurb: t("toolkit.blurb.maintenance") },
    { id: "citations", label: t("toolkit.tab.citations"), icon: FileSearch, blurb: t("toolkit.blurb.citations") },
  ];

  return (
    <div className="min-h-[calc(100vh-73px)] bg-gray-50/50 px-4 py-10 sm:px-6 sm:py-12">
      <div className="mx-auto max-w-4xl">
        <header className="mb-8 animate-fade-in-up">
          <h1 className="font-serif text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
            {t("toolkit.title")}
          </h1>
          <p className="mt-2 max-w-2xl text-gray-600">{t("toolkit.subtitle")}</p>
        </header>

        {/* Tabs */}
        <div
          role="tablist"
          aria-label={t("toolkit.sections")}
          className="mb-6 grid grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-3"
        >
          {tabs.map(({ id, label, icon: Icon, blurb }) => (
            <button
              key={id}
              role="tab"
              aria-selected={tab === id}
              onClick={() => {
                setTab(id);
                setError(null);
              }}
              className={cn(
                "flex items-start gap-3 rounded-xl border p-3.5 text-left transition-colors",
                tab === id
                  ? "border-slate-900 bg-slate-900 text-white"
                  : "border-gray-200 bg-white text-gray-700 hover:border-gray-300",
              )}
            >
              <Icon className="mt-0.5 h-5 w-5 shrink-0" />
              <span className="min-w-0">
                <span className="block text-sm font-semibold">{label}</span>
                <span
                  className={cn(
                    "block text-xs",
                    tab === id ? "text-white/70" : "text-gray-500",
                  )}
                >
                  {blurb}
                </span>
              </span>
            </button>
          ))}
        </div>

        {canShareResult && (
          <div className="mb-5 flex flex-wrap items-center gap-2">
            <button
              onClick={shareLink}
              className="flex items-center gap-1.5 rounded-full border border-gray-200 bg-white px-3.5 py-2 text-xs font-medium text-gray-700 transition-colors hover:bg-gray-50"
            >
              {shared ? (
                <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600" />
              ) : (
                <Share2 className="h-3.5 w-3.5" />
              )}
              {shared ? "Link copied" : "Copy shareable link"}
            </button>
            <button
              onClick={shareOnWhatsApp}
              className="flex items-center gap-1.5 rounded-full border border-emerald-200 bg-emerald-50 px-3.5 py-2 text-xs font-medium text-emerald-800 transition-colors hover:bg-emerald-100"
            >
              <MessageCircle className="h-3.5 w-3.5" />
              Send on WhatsApp
            </button>
          </div>
        )}

        {error && (
          <div className="mb-5 flex items-start gap-2 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">
            <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
            <p>{error}</p>
          </div>
        )}

        {/* ── Deadline ─────────────────────────────────────────────── */}
        {tab === "deadline" && (
          <div className="space-y-5 animate-fade-in-up">
            <SectionCard>
              <div className="space-y-4">
                <div>
                  <Label>What are you trying to file?</Label>
                  <select
                    value={limId}
                    onChange={(e) => {
                      setLimId(e.target.value);
                      setLimResult(null);
                    }}
                    className={inputClass}
                  >
                    <option value="">Select a matter…</option>
                    {grouped(limRules).map(([category, rules]) => (
                      <optgroup key={category} label={category}>
                        {rules.map((r) => (
                          <option key={r.id} value={r.id}>
                            {r.label}
                          </option>
                        ))}
                      </optgroup>
                    ))}
                  </select>
                </div>

                {selectedLimRule && (
                  <div className="rounded-xl bg-gray-50 px-4 py-3">
                    <p className="text-sm text-gray-700">
                      <strong>The clock starts from</strong> {selectedLimRule.trigger}.
                    </p>
                    <p className="mt-1 text-xs text-gray-500">{selectedLimRule.citation}</p>
                  </div>
                )}

                <div>
                  <Label>Date that happened</Label>
                  <input
                    type="date"
                    value={limDate}
                    max={new Date().toISOString().slice(0, 10)}
                    onChange={(e) => {
                      setLimDate(e.target.value);
                      setLimResult(null);
                    }}
                    className={inputClass}
                  />
                </div>

                <button
                  type="button"
                  onClick={() =>
                    requireAuth(async () => {
                      const r = await post("/api/tools/limitation", {
                        rule_id: limId,
                        event_date: limDate,
                      });
                      if (r) {
                        setLimResult(r);
                        setComputedOffline(false);
                        return;
                      }
                      // The server did not answer. This is arithmetic over a
                      // table we already hold, so refusing to answer would be a
                      // choice rather than a limitation.
                      const cached = readCachedBundle();
                      if (cached) {
                        try {
                          setLimResult(
                            calculateLocally(cached, limId, limDate) as unknown as LimitationResult,
                          );
                          setComputedOffline(true);
                          setError(null);
                        } catch {
                          /* Unknown rule in an old cache — leave the server error up. */
                        }
                      }
                    }, t("auth.reason.deadline"))
                  }
                  disabled={!limId || !limDate || busy}
                  className="flex w-full items-center justify-center gap-2 rounded-full bg-black px-6 py-3 text-sm font-medium text-white transition-colors hover:bg-gray-800 disabled:opacity-40 sm:w-auto"
                >
                  {busy ? <Loader2 className="h-4 w-4 animate-spin" /> : <Clock className="h-4 w-4" />}
                  {busy ? t("toolkit.working") : t("toolkit.calculateDeadline")}
                </button>
              </div>
            </SectionCard>

            {limResult && computedOffline && (
              <div className="flex items-start gap-2 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
                <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
                <span>{t("toolkit.offlineNotice")}</span>
              </div>
            )}

            {limResult && (
              <SectionCard className="animate-fade-in-up">
                <h2 className="mb-4 font-serif text-xl font-bold text-slate-900">
                  {limResult.label}
                </h2>
                <DeadlineDial result={limResult} />
                <FilingDayPanel result={limResult} calendar={calendar} />
                {limResult.notes.length > 0 && (
                  <ul className="mt-4 space-y-2">
                    {limResult.notes.map((note, i) => (
                      <li key={i} className="flex gap-2 text-sm text-gray-600">
                        <span className="mt-2 h-1 w-1 shrink-0 rounded-full bg-gray-400" />
                        {note}
                      </li>
                    ))}
                  </ul>
                )}
                <p className="mt-4 border-t border-gray-100 pt-3 text-xs text-gray-500">
                  {limResult.citation}
                </p>
              </SectionCard>
            )}
          </div>
        )}

        {/* ── Forum ────────────────────────────────────────────────── */}
        {tab === "forum" && (
          <div className="space-y-5 animate-fade-in-up">
            <SectionCard>
              <div className="space-y-4">
                <div>
                  <Label>What is the problem?</Label>
                  <select
                    value={forumId}
                    onChange={(e) => {
                      setForumId(e.target.value);
                      setForumResult(null);
                    }}
                    className={inputClass}
                  >
                    <option value="">Select…</option>
                    {grouped(forumRules).map(([category, rules]) => (
                      <optgroup key={category} label={category}>
                        {rules.map((r) => (
                          <option key={r.id} value={r.id}>
                            {r.label}
                          </option>
                        ))}
                      </optgroup>
                    ))}
                  </select>
                </div>

                {selectedForumRule?.value_question && (
                  <div>
                    <Label>{selectedForumRule.value_question}</Label>
                    <input
                      type="number"
                      inputMode="numeric"
                      value={claimValue}
                      onChange={(e) => setClaimValue(e.target.value)}
                      placeholder="e.g. 45000"
                      className={inputClass}
                    />
                  </div>
                )}

                <button
                  onClick={() =>
                    requireAuth(async () => {
                      const r = await post("/api/tools/forum", {
                        rule_id: forumId,
                        claim_value: claimValue ? Number(claimValue) : null,
                      });
                      if (r) setForumResult(r);
                    }, t("auth.reason.forum"))
                  }
                  disabled={!forumId || busy}
                  className="flex w-full items-center justify-center gap-2 rounded-full bg-black px-6 py-3 text-sm font-medium text-white transition-colors hover:bg-gray-800 disabled:opacity-40 sm:w-auto"
                >
                  {busy ? <Loader2 className="h-4 w-4 animate-spin" /> : <MapPin className="h-4 w-4" />}
                  {busy ? t("toolkit.working") : t("toolkit.findForum")}
                </button>
              </div>
            </SectionCard>

            {forumResult && (
              <SectionCard className="animate-fade-in-up">
                <div className="mb-4 flex flex-wrap items-center gap-2">
                  <Scale className="h-5 w-5 text-amber-600" />
                  <h2 className="font-serif text-xl font-bold text-slate-900">
                    {forumResult.forum.name}
                  </h2>
                  {forumResult.value_tier && (
                    <span className="rounded-full bg-amber-50 px-2.5 py-0.5 text-xs font-medium text-amber-800">
                      {forumResult.value_tier}
                    </span>
                  )}
                </div>

                <dl className="grid gap-4 sm:grid-cols-2">
                  {[
                    ["Where", forumResult.forum.where],
                    ["Fee", forumResult.forum.fee],
                    ["How to file", forumResult.forum.how_to_file],
                    ["Do you need a lawyer?", forumResult.forum.lawyer_needed],
                    ["Typical duration", forumResult.forum.typical_duration],
                  ]
                    .filter(([, v]) => v)
                    .map(([term, value]) => (
                      <div key={term}>
                        <dt className="text-xs font-semibold uppercase tracking-wider text-gray-400">
                          {term}
                        </dt>
                        <dd className="mt-1 text-sm text-gray-700">{value}</dd>
                      </div>
                    ))}
                </dl>

                <div className="mt-5 border-t border-gray-100 pt-4">
                  <h3 className="mb-2 text-sm font-semibold text-gray-900">What to bring</h3>
                  <ul className="space-y-1.5">
                    {forumResult.forum.documents.map((d, i) => (
                      <li key={i} className="flex gap-2 text-sm text-gray-600">
                        <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-gray-300" />
                        {d}
                      </li>
                    ))}
                  </ul>
                </div>

                {forumResult.forum.notes.length > 0 && (
                  <div className="mt-4 rounded-xl bg-amber-50 px-4 py-3">
                    <ul className="space-y-1.5">
                      {forumResult.forum.notes.map((n, i) => (
                        <li key={i} className="text-sm text-amber-900">
                          {n}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {forumResult.limitation.length > 0 && (
                  <div className="mt-4 border-t border-gray-100 pt-4">
                    <h3 className="mb-2 text-sm font-semibold text-gray-900">
                      Deadlines that apply
                    </h3>
                    {forumResult.limitation.map((l) => (
                      <button
                        key={l.id}
                        onClick={() => {
                          setLimId(l.id);
                          setLimResult(null);
                          setTab("deadline");
                        }}
                        className="mb-1.5 flex w-full items-center gap-2 rounded-lg bg-gray-50 px-3 py-2 text-left text-sm text-gray-700 transition-colors hover:bg-gray-100"
                      >
                        <CalendarClock className="h-4 w-4 shrink-0 text-gray-400" />
                        <span className="flex-1">{l.label}</span>
                        <span className="text-xs text-gray-400">Calculate →</span>
                      </button>
                    ))}
                  </div>
                )}
              </SectionCard>
            )}
          </div>
        )}

        {/* ── Draft ────────────────────────────────────────────────── */}
        {tab === "draft" && (
          <div className="space-y-5 animate-fade-in-up">
            <SectionCard>
              <Label>Which document?</Label>
              <select
                value={templateId}
                onChange={(e) => {
                  setTemplateId(e.target.value);
                  setFormData({});
                  setDoc(null);
                }}
                className={inputClass}
              >
                <option value="">Select a document…</option>
                {grouped(templates).map(([category, items]) => (
                  <optgroup key={category} label={category}>
                    {items.map((t) => (
                      <option key={t.id} value={t.id}>
                        {t.title}
                      </option>
                    ))}
                  </optgroup>
                ))}
              </select>

              {activeTemplate && (
                <>
                  <p className="mt-3 text-sm text-gray-600">{activeTemplate.description}</p>
                  <p className="mt-1 text-xs text-gray-500">
                    {activeTemplate.citation}
                    {activeTemplate.fee && ` · Fee: ${activeTemplate.fee}`}
                  </p>

                  <div className="mt-5 grid gap-4 sm:grid-cols-2">
                    {activeTemplate.fields.map((f) => (
                      <div
                        key={f.name}
                        className={f.kind === "textarea" ? "sm:col-span-2" : undefined}
                      >
                        <Label>
                          {f.label}
                          {!f.required && (
                            <span className="ml-1 font-normal text-gray-400">(optional)</span>
                          )}
                        </Label>
                        {f.kind === "textarea" ? (
                          <textarea
                            rows={4}
                            value={formData[f.name] ?? ""}
                            placeholder={f.placeholder}
                            onChange={(e) =>
                              setFormData((p) => ({ ...p, [f.name]: e.target.value }))
                            }
                            className={cn(inputClass, "resize-y")}
                          />
                        ) : (
                          <input
                            type={f.kind === "number" ? "number" : f.kind}
                            value={formData[f.name] ?? ""}
                            placeholder={f.placeholder}
                            onChange={(e) =>
                              setFormData((p) => ({ ...p, [f.name]: e.target.value }))
                            }
                            className={inputClass}
                          />
                        )}
                        {f.help && <p className="mt-1 text-xs text-gray-500">{f.help}</p>}
                      </div>
                    ))}
                  </div>

                  <button
                    onClick={() =>
                      requireAuth(async () => {
                        const r = await post("/api/tools/documents", {
                          template_id: templateId,
                          data: formData,
                        });
                        if (r) setDoc(r);
                      }, t("auth.reason.draft"))
                    }
                    disabled={busy}
                    className="mt-5 flex w-full items-center justify-center gap-2 rounded-full bg-black px-6 py-3 text-sm font-medium text-white transition-colors hover:bg-gray-800 disabled:opacity-40 sm:w-auto"
                  >
                    {busy ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <FileText className="h-4 w-4" />
                    )}
                    {busy ? t("toolkit.working") : t("toolkit.generateDocument")}
                  </button>
                </>
              )}
            </SectionCard>

            {doc && (
              <SectionCard className="animate-fade-in-up print:border-0 print:p-0">
                <div className="mb-4 flex flex-wrap items-center justify-between gap-3 print:hidden">
                  <h2 className="font-serif text-xl font-bold text-slate-900">{doc.title}</h2>
                  <div className="flex gap-2">
                    <button
                      onClick={copyDoc}
                      className="flex items-center gap-1.5 rounded-full border border-gray-200 px-3.5 py-2 text-xs font-medium text-gray-700 transition-colors hover:bg-gray-50"
                    >
                      {copied ? (
                        <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600" />
                      ) : (
                        <Copy className="h-3.5 w-3.5" />
                      )}
                      {copied ? "Copied" : "Copy"}
                    </button>
                    <button
                      onClick={downloadDoc}
                      className="flex items-center gap-1.5 rounded-full border border-gray-200 px-3.5 py-2 text-xs font-medium text-gray-700 transition-colors hover:bg-gray-50"
                    >
                      <Download className="h-3.5 w-3.5" />
                      Download
                    </button>
                    <button
                      onClick={() => window.print()}
                      className="flex items-center gap-1.5 rounded-full border border-gray-200 px-3.5 py-2 text-xs font-medium text-gray-700 transition-colors hover:bg-gray-50"
                    >
                      <Printer className="h-3.5 w-3.5" />
                      Print
                    </button>
                  </div>
                </div>

                {doc.missing.length > 0 && (
                  <div className="mb-4 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 print:hidden">
                    <p className="text-sm font-medium text-amber-900">
                      Blanks left in the document
                    </p>
                    <p className="mt-1 text-sm text-amber-800">
                      {doc.missing.join(", ")} — fill these in above, or complete them by
                      hand after printing.
                    </p>
                  </div>
                )}

                <pre className="overflow-x-auto whitespace-pre-wrap rounded-xl bg-gray-50 p-5 font-mono text-[13px] leading-relaxed text-gray-800 print:bg-white print:p-0 print:text-black">
                  {doc.body}
                </pre>

                {doc.after.length > 0 && (
                  <div className="mt-5 print:hidden">
                    <h3 className="mb-2 text-sm font-semibold text-gray-900">
                      After you print it
                    </h3>
                    <ol className="space-y-2">
                      {doc.after.map((step, i) => (
                        <li key={i} className="flex gap-2.5 text-sm text-gray-600">
                          <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-gray-100 text-[11px] font-semibold text-gray-600">
                            {i + 1}
                          </span>
                          {step}
                        </li>
                      ))}
                    </ol>
                  </div>
                )}
              </SectionCard>
            )}
          </div>
        )}
        {tab === "plan" && (
          <div className="animate-fade-in-up">
            <CasePlanTool
              onError={setError}
              initialSituation={planSituation}
              initialDate={limDate}
              onOpenTemplate={(id) => {
                setTemplateId(id);
                setTab("draft");
                setError(null);
                window.scrollTo({ top: 0, behavior: "smooth" });
              }}
            />
          </div>
        )}

        {tab === "timeline" && (
          <div className="animate-fade-in-up">
            <TimelineTool onError={setError} />
          </div>
        )}

        {tab === "fees" && (
          <div className="animate-fade-in-up">
            <FeesTool onError={setError} />
          </div>
        )}

        {tab === "tracker" && (
          <div className="animate-fade-in-up">
            <TrackerTool onError={setError} />
          </div>
        )}

        {tab === "stampduty" && (
          <div className="animate-fade-in-up">
            <StampDutyTool onError={setError} />
          </div>
        )}

        {tab === "maintenance" && (
          <div className="animate-fade-in-up">
            <MaintenanceTool onError={setError} />
          </div>
        )}

        {tab === "citations" && (
          <div className="animate-fade-in-up">
            <CitationsTool onError={setError} />
          </div>
        )}
      </div>
    </div>
  );
}
