"use client";

import { useState, useRef, useCallback } from "react";
import { useAuthGate } from "@/lib/auth/AuthGate";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  FileText,
  Play,
  Loader2,
  Scale,
  Sparkles,
  Upload,
  X,
  AlertTriangle,
  CheckCircle2,
  Shield,
  BookOpen,
  Users,
  ChevronRight,
  CalendarClock,
  ListChecks,
  Library,
} from "lucide-react";
import { VoiceButton } from "@/components/VoiceButton";
import { SpeakButton } from "@/components/SpeakButton";
import { useLanguage } from "@/lib/i18n/LanguageProvider";
import { LOCALE_LIST, normalizeLocale } from "@/lib/i18n/locales";

// ── Types ──────────────────────────────────────────────────────────────────
interface ClauseItem {
  title: string;
  content: string;
  risk_level: "low" | "medium" | "high";
}

interface AnalysisResult {
  summary: string;
  document_type: string;
  word_count: number;
  char_count: number;
  clauses: ClauseItem[];
  key_entities: string[];
  risk_flags: string[];
  recommendations: string[];
  /** Concrete next steps, in order. */
  action_steps: string[];
  /** Dates and periods found in the text that may be deadlines. */
  key_dates: string[];
  /** Statute passages the analysis was grounded in. */
  sources: { title: string; citation: string; url: string }[];
  /** ollama | gemini | heuristic */
  provider: string;
  /** True while a model is still improving this result in the background. */
  refining: boolean;
  refine_id: string | null;
}

interface AnalyzeResponse {
  status: string;
  data: AnalysisResult;
}

// ── Constants ──────────────────────────────────────────────────────────────
const API_BASE = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000") + "";
const ACCEPTED_TYPES = [
  "application/pdf",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  "text/plain",
];
const ACCEPT_STRING = ".pdf,.docx,.txt";

// ── Risk summary ───────────────────────────────────────────────────────────
/**
 * Severity at a glance.
 *
 * A list of clauses tells you nothing about the shape of the document until
 * you have read all of it. Encoding the distribution as width — not just a
 * number — means "this contract is mostly high risk" lands before any reading
 * happens. Counts stay visible because colour alone is not an accessible
 * signal, and the segments carry text labels for screen readers.
 */
function RiskSummary({ clauses }: { clauses: ClauseItem[] }) {
  const counts = {
    high: clauses.filter((c) => c.risk_level === "high").length,
    medium: clauses.filter((c) => c.risk_level === "medium").length,
    low: clauses.filter((c) => c.risk_level === "low").length,
  };
  const total = clauses.length;
  if (!total) return null;

  const segments = [
    { key: "high", label: "High", count: counts.high, bar: "bg-red-500", dot: "bg-red-500" },
    { key: "medium", label: "Medium", count: counts.medium, bar: "bg-amber-500", dot: "bg-amber-500" },
    { key: "low", label: "Low", count: counts.low, bar: "bg-emerald-500", dot: "bg-emerald-500" },
  ].filter((s) => s.count > 0);

  return (
    <div className="rounded-xl border border-border/50 bg-background/50 p-4">
      <div className="flex items-baseline justify-between mb-2.5">
        <h3 className="text-sm font-semibold">Risk profile</h3>
        <span className="text-xs text-muted-foreground tabular-nums">
          {total} clause{total === 1 ? "" : "s"}
        </span>
      </div>

      <div
        className="flex h-2.5 w-full overflow-hidden rounded-full bg-muted"
        role="img"
        aria-label={segments.map((s) => `${s.count} ${s.label} risk`).join(", ")}
      >
        {segments.map((s) => (
          <div
            key={s.key}
            className={`${s.bar} risk-segment`}
            style={{ width: `${(s.count / total) * 100}%` }}
          />
        ))}
      </div>

      <div className="mt-2.5 flex flex-wrap gap-x-4 gap-y-1">
        {segments.map((s) => (
          <span key={s.key} className="flex items-center gap-1.5 text-xs text-muted-foreground">
            <span className={`h-2 w-2 rounded-full ${s.dot}`} />
            <span className="tabular-nums font-medium text-foreground">{s.count}</span>
            {s.label}
          </span>
        ))}
      </div>
    </div>
  );
}

// ── Risk badge helper ──────────────────────────────────────────────────────
function RiskBadge({ level }: { level: string }) {
  const config = {
    high: "bg-red-500/10 text-red-600 dark:text-red-400 border-red-500/20",
    medium:
      "bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20",
    low: "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20",
  }[level] ?? "bg-muted text-muted-foreground border-border";

  return (
    <span
      className={`inline-flex items-center rounded-full border px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider ${config}`}
    >
      {level}
    </span>
  );
}

// ── Main Page ──────────────────────────────────────────────────────────────
export default function Home() {
  const { requireAuth } = useAuthGate();
  const [isProcessing, setIsProcessing] = useState(false);
  const [text, setText] = useState("");
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  /** Id of the refinement we still care about; a new run invalidates the old. */
  const refineAbortRef = useRef<string | null>(null);

  // The output language is the app-wide locale rather than page-local state, so
  // the picker here and the one in the navbar can never disagree.
  const { locale, meta, setLocale, t } = useLanguage();

  // ── File handling ──────────────────────────────────────────────────────
  const handleFileSelect = useCallback((file: File) => {
    if (!ACCEPTED_TYPES.includes(file.type)) {
      setError("Unsupported file type. Please upload a PDF, DOCX, or TXT file.");
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      setError("File too large. Maximum size is 10 MB.");
      return;
    }
    setUploadedFile(file);
    setError(null);
    setText(""); // Clear text when file is uploaded
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      const file = e.dataTransfer.files[0];
      if (file) handleFileSelect(file);
    },
    [handleFileSelect]
  );

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const removeFile = useCallback(() => {
    setUploadedFile(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  }, []);

  // ── Background refinement ──────────────────────────────────────────────
  /**
   * Poll until the model-enriched analysis is ready, then replace the
   * deterministic one in place. Gives up quietly — the result already on
   * screen is a complete, usable analysis, not a placeholder.
   */
  const pollForRefinement = useCallback(async (refineId: string) => {
    const started = Date.now();
    const deadline = 8 * 60 * 1000;

    while (Date.now() - started < deadline) {
      await new Promise((resolve) => setTimeout(resolve, 3000));
      if (refineAbortRef.current !== refineId) return; // superseded by a new run

      try {
        const res = await fetch(`${API_BASE}/api/analyze/refine/${refineId}`);
        if (!res.ok) return;
        const json: { status: string; data: AnalysisResult | null } = await res.json();

        if (json.status === "ready" && json.data) {
          if (refineAbortRef.current === refineId) setResult(json.data);
          return;
        }
        if (json.status === "gone") return;
      } catch {
        return; // network gone; keep what we have
      }
    }
  }, []);

  // ── Process document ───────────────────────────────────────────────────
  const runAnalysis = async () => {
    setIsProcessing(true);
    setError(null);
    setResult(null);

    try {
      const formData = new FormData();

      if (uploadedFile) {
        formData.append("file", uploadedFile);
      } else if (text.trim()) {
        formData.append("raw_text", text.trim());
      }
      formData.append("language", meta.gemini);

      const res = await fetch(`${API_BASE}/api/analyze`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: "Server error" }));
        throw new Error(err.detail || `Request failed with status ${res.status}`);
      }

      const json: AnalyzeResponse = await res.json();
      setResult(json.data);

      // The first response is the deterministic breakdown, which arrives in
      // well under a second. A model then improves it behind the scenes; poll
      // for that and swap it in without the reader ever waiting on a spinner.
      if (json.data.refining && json.data.refine_id) {
        refineAbortRef.current = json.data.refine_id;
        pollForRefinement(json.data.refine_id);
      } else {
        refineAbortRef.current = null;
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : "An unexpected error occurred";
      setError(message);
    } finally {
      setIsProcessing(false);
    }
  };

  // The document stays pasted and the options stay chosen while they sign in,
  // and the analysis then runs by itself.
  const handleProcess = () =>
    requireAuth(runAnalysis, "Sign in to analyse this document.");

  const hasInput = uploadedFile !== null || text.trim().length > 0;

  return (
    <div className="min-h-[calc(100vh-73px)] w-full bg-gray-50 p-4 lg:p-8 flex items-center justify-center animate-fade-in-up">
      <div className="h-[85vh] w-full max-w-7xl mx-auto rounded-[2rem] bg-white shadow-xl border border-gray-100 overflow-hidden">
          <div className="flex flex-col lg:flex-row h-full items-stretch">
            {/* ─── Left Pane: Input ─── */}
            <div className="flex flex-col w-full lg:w-1/2 bg-background/30 border-b lg:border-b-0 lg:border-r border-border/20 overflow-y-auto">
            <div className="flex flex-col h-full p-5 lg:p-6 gap-4">
              {/* Section header */}
              <div className="flex flex-col gap-1 animate-fade-in-up">
                <div className="flex items-center gap-2">
                  <div className="flex h-6 w-6 items-center justify-center rounded-md bg-primary/10">
                    <FileText className="h-3.5 w-3.5 text-primary" />
                  </div>
                  <h2 className="text-base font-semibold tracking-tight">
                    Legal Document
                  </h2>
                </div>
                <p className="text-sm text-muted-foreground pl-8">
                  Upload a file or paste raw legal text for analysis.
                </p>
              </div>

              {/* ── File Upload Zone ── */}
              <div className="animate-fade-in-up" style={{ animationDelay: "80ms" }}>
                <div
                  onDrop={handleDrop}
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onClick={() => !uploadedFile && fileInputRef.current?.click()}
                  className={`
                    relative flex flex-col items-center justify-center rounded-xl border-2 border-dashed p-5 transition-all duration-300 cursor-pointer
                    ${isDragging
                      ? "border-primary bg-primary/5 scale-[1.01]"
                      : uploadedFile
                        ? "border-emerald-500/40 bg-emerald-500/5 cursor-default"
                        : "border-border/60 bg-muted/20 hover:border-primary/40 hover:bg-muted/30"
                    }
                  `}
                >
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept={ACCEPT_STRING}
                    className="hidden"
                    onChange={(e) => {
                      const file = e.target.files?.[0];
                      if (file) handleFileSelect(file);
                    }}
                  />

                  {uploadedFile ? (
                    <div className="flex items-center gap-3 w-full">
                      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-emerald-500/10">
                        <CheckCircle2 className="h-5 w-5 text-emerald-500" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate">
                          {uploadedFile.name}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {(uploadedFile.size / 1024).toFixed(1)} KB •{" "}
                          {uploadedFile.type.split("/").pop()?.toUpperCase()}
                        </p>
                      </div>
                      <Button
                        variant="ghost"
                        size="icon-sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          removeFile();
                        }}
                        className="shrink-0 text-muted-foreground hover:text-destructive cursor-pointer"
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  ) : (
                    <>
                      <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10 mb-2">
                        <Upload className="h-5 w-5 text-primary" />
                      </div>
                      <p className="text-sm font-medium text-foreground">
                        Drop your file here, or{" "}
                        <span className="text-primary underline underline-offset-2">
                          browse
                        </span>
                      </p>
                      <p className="text-xs text-muted-foreground mt-0.5">
                        PDF, DOCX, or TXT • Max 10 MB
                      </p>
                    </>
                  )}
                </div>
              </div>

              {/* ── Divider ── */}
              <div className="flex items-center gap-3 animate-fade-in-up" style={{ animationDelay: "120ms" }}>
                <div className="flex-1 h-px bg-border/50" />
                <span className="text-xs text-muted-foreground/60 font-medium">
                  OR PASTE TEXT
                </span>
                <div className="flex-1 h-px bg-border/50" />
              </div>

              {/* ── Text area ── */}
              <div
                className="flex-1 relative flex flex-col animate-fade-in-up min-h-0"
                style={{ animationDelay: "160ms" }}
              >
                <Textarea
                  id="legal-text-input"
                  placeholder="Paste the legal contract, case file, or regulatory text here…"
                  className="flex-1 resize-none bg-muted/30 font-mono text-sm leading-relaxed p-4 focus-visible:ring-1 focus-visible:ring-primary/40 rounded-xl border-border/50 transition-all duration-300 hover:border-primary/30 hover:bg-muted/40"
                  value={text}
                  onChange={(e) => {
                    setText(e.target.value);
                    if (e.target.value.trim()) {
                      setUploadedFile(null); // Clear file when typing
                      if (fileInputRef.current) fileInputRef.current.value = "";
                    }
                  }}
                  disabled={!!uploadedFile}
                />
                <div className="absolute bottom-3 right-3 text-[11px] text-muted-foreground/60 tabular-nums pointer-events-none select-none">
                  {text.length.toLocaleString()} chars
                </div>
              </div>

              {/* ── Error message ── */}
              {error && (
                <div className="flex items-start gap-2 rounded-lg bg-destructive/10 border border-destructive/20 px-3 py-2.5 text-sm text-destructive animate-fade-in-up">
                  <AlertTriangle className="h-4 w-4 shrink-0 mt-0.5" />
                  <p>{error}</p>
                </div>
              )}

              {/* ── Action bar ── */}
              <div
                className="flex items-center justify-between pt-1 animate-fade-in-up"
                style={{ animationDelay: "200ms" }}
              >
                <div className="flex items-center gap-2">
                  {/* Dictation — lets a user describe their document aloud
                      instead of typing it in a script they may not write. */}
                  <VoiceButton
                    onTranscript={(spoken) =>
                      setText((prev) => (prev ? `${prev} ${spoken}` : spoken))
                    }
                    onError={setError}
                    idleLabelKey="analyze.dictate"
                    showInterim
                    disabled={isProcessing || !!uploadedFile}
                  />
                  <p className="text-xs text-muted-foreground/70 hidden sm:block">
                    Supports contracts, judgments, statutes & more
                  </p>
                </div>
                <div className="flex items-center gap-3 w-full sm:w-auto">
                  <Select
                    value={locale}
                    onValueChange={(value) => setLocale(normalizeLocale(value))}
                    disabled={isProcessing}
                  >
                    <SelectTrigger className="w-[140px] h-10 rounded-full bg-background/50 border-border/50">
                      <SelectValue placeholder={t("analyze.language")} />
                    </SelectTrigger>
                    <SelectContent>
                      {LOCALE_LIST.map((item) => (
                        <SelectItem key={item.code} value={item.code}>
                          {item.native}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <Button
                    id="process-document-btn"
                    onClick={handleProcess}
                    disabled={isProcessing || !hasInput}
                    size="lg"
                    className="w-full sm:w-auto h-10 px-6 rounded-full shadow-md shadow-primary/20 hover:shadow-lg hover:shadow-primary/30 transition-all duration-300 cursor-pointer"
                  >
                    {isProcessing ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        {t("analyze.processing")}
                      </>
                    ) : (
                      <>
                        <Play className="mr-2 h-4 w-4" />
                        {t("analyze.process")}
                      </>
                    )}
                  </Button>
                </div>
              </div>
            </div>
          </div>

          {/* ─── Right Pane: Output ─── */}
          <div className="flex flex-col w-full lg:w-1/2 bg-background/10 backdrop-blur-md overflow-y-auto">
            <div className="flex flex-col h-full p-5 lg:p-6 gap-4">
              {/* Section header */}
              <div className="flex flex-col gap-1 animate-fade-in-up">
                <div className="flex items-center gap-2">
                  <div className="flex h-6 w-6 items-center justify-center rounded-md bg-primary/10">
                    <Sparkles className="h-3.5 w-3.5 text-primary" />
                  </div>
                  <h2 className="text-base font-semibold tracking-tight">
                    Analysis & Output
                  </h2>
                </div>
                <p className="text-sm text-muted-foreground pl-8">
                  {result
                    ? `${result.document_type} • ${result.word_count.toLocaleString()} words`
                    : "AI-generated insights and extraction results."}
                </p>
              </div>

              {/* Output area */}
              <div className="flex-1 rounded-xl border border-white/5 p-6 bg-background/40 overflow-auto shadow-inner animate-fade-in-up" style={{ animationDelay: "100ms" }}>
                {isProcessing ? (
                  /* ── Skeleton loader ── */
                  <div className="space-y-6">
                    <div className="space-y-2.5">
                      <div className="skeleton-shimmer h-5 w-2/5 rounded-lg" />
                      <div className="skeleton-shimmer h-3.5 w-1/4 rounded-md" />
                    </div>
                    <div className="space-y-3 pt-2">
                      <div className="skeleton-shimmer h-[120px] w-full rounded-xl" />
                    </div>
                    <div className="space-y-2.5 pt-2">
                      <div className="skeleton-shimmer h-3.5 w-full rounded-md" />
                      <div className="skeleton-shimmer h-3.5 w-[92%] rounded-md" />
                      <div className="skeleton-shimmer h-3.5 w-[96%] rounded-md" />
                      <div className="skeleton-shimmer h-3.5 w-[88%] rounded-md" />
                      <div className="skeleton-shimmer h-3.5 w-[82%] rounded-md" />
                    </div>
                    <div className="space-y-3 pt-2">
                      <div className="skeleton-shimmer h-4 w-1/3 rounded-md" />
                      <div className="grid grid-cols-2 gap-3">
                        <div className="skeleton-shimmer h-20 rounded-xl" />
                        <div className="skeleton-shimmer h-20 rounded-xl" />
                      </div>
                    </div>
                    <div className="flex items-center gap-2 pt-4 text-xs text-muted-foreground">
                      <Loader2 className="h-3 w-3 animate-spin text-primary" />
                      <span>Analyzing document structure and clauses…</span>
                    </div>
                  </div>
                ) : result ? (
                  /* ── Analysis Results ── */
                  <div className="space-y-6 animate-fade-in-up">
                    {/* How this analysis was produced. Worth stating plainly:
                        a reader deciding whether to trust it should know
                        whether a model was involved at all. */}
                    <div className="flex flex-wrap items-center gap-2">
                      {result.refining ? (
                        <span className="inline-flex items-center gap-1.5 rounded-full bg-primary/10 px-2.5 py-1 text-[11px] font-medium text-primary">
                          <Loader2 className="h-3 w-3 animate-spin" />
                          Ready to read — improving it with the local model…
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1.5 rounded-full bg-muted px-2.5 py-1 text-[11px] font-medium text-muted-foreground">
                          <Shield className="h-3 w-3" />
                          {result.provider === "heuristic"
                            ? "Rule-based analysis · no model used"
                            : result.provider === "ollama"
                              ? "Analysed by a model on this machine"
                              : "Analysed by a hosted model"}
                        </span>
                      )}
                    </div>

                    <RiskSummary clauses={result.clauses} />

                    {/* Summary card */}
                    <div className="rounded-xl bg-gradient-to-br from-primary/5 to-primary/[0.02] border border-primary/10 p-4">
                      <div className="flex items-center justify-between gap-2 mb-2">
                        <div className="flex items-center gap-2">
                          <BookOpen className="h-4 w-4 text-primary" />
                          <h3 className="text-sm font-semibold">Summary</h3>
                        </div>
                        {/* The summary is the one section a non-reader most
                            needs; the AI has already written it in their
                            language, so it can be played back directly. */}
                        <SpeakButton text={result.summary} variant="labelled" />
                      </div>
                      <p className="text-sm leading-relaxed text-muted-foreground">
                        {result.summary}
                      </p>
                      <div className="flex gap-3 mt-3 text-xs text-muted-foreground/70">
                        <span>{result.word_count.toLocaleString()} words</span>
                        <span>•</span>
                        <span>{result.char_count.toLocaleString()} characters</span>
                        <span>•</span>
                        <span>{result.clauses.length} clauses</span>
                      </div>
                    </div>

                    {/* Key Entities */}
                    {result.key_entities.length > 0 && (
                      <div>
                        <div className="flex items-center gap-2 mb-2.5">
                          <Users className="h-4 w-4 text-primary" />
                          <h3 className="text-sm font-semibold">Key Entities</h3>
                        </div>
                        <div className="flex flex-wrap gap-1.5">
                          {result.key_entities.map((entity) => (
                            <span
                              key={entity}
                              className="rounded-full bg-secondary px-2.5 py-1 text-xs font-medium text-secondary-foreground"
                            >
                              {entity}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Clauses */}
                    {result.clauses.length > 0 && (
                      <div>
                        <div className="flex items-center gap-2 mb-2.5">
                          <FileText className="h-4 w-4 text-primary" />
                          <h3 className="text-sm font-semibold">
                            Detected Clauses
                          </h3>
                        </div>
                        <div className="space-y-2">
                          {result.clauses.map((clause, i) => (
                            <div
                              key={i}
                              className="rounded-lg border border-border/50 p-3 bg-background/50 hover:bg-muted/20 transition-colors"
                            >
                              <div className="flex items-center justify-between mb-1.5">
                                <span className="text-sm font-medium flex items-center gap-1.5">
                                  <ChevronRight className="h-3.5 w-3.5 text-primary" />
                                  {clause.title}
                                </span>
                                <RiskBadge level={clause.risk_level} />
                              </div>
                              <p className="text-xs text-muted-foreground leading-relaxed pl-5">
                                {clause.content}
                              </p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Dates and deadlines — extracted deterministically, so
                        these are exactly what the document says, not a
                        paraphrase. Missing one is what costs people cases. */}
                    {result.key_dates.length > 0 && (
                      <div>
                        <div className="flex items-center gap-2 mb-2.5">
                          <CalendarClock className="h-4 w-4 text-primary" />
                          <h3 className="text-sm font-semibold">Dates &amp; deadlines</h3>
                        </div>
                        <div className="flex flex-wrap gap-1.5">
                          {result.key_dates.map((date, i) => (
                            <span
                              key={i}
                              className="rounded-md border border-primary/20 bg-primary/5 px-2 py-1 text-xs tabular-nums text-foreground"
                            >
                              {date}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Risk Flags */}
                    {result.risk_flags.length > 0 && (
                      <div>
                        <div className="flex items-center gap-2 mb-2.5">
                          <AlertTriangle className="h-4 w-4 text-amber-500" />
                          <h3 className="text-sm font-semibold">Risk Flags</h3>
                        </div>
                        <div className="space-y-1.5">
                          {result.risk_flags.map((flag, i) => (
                            <div
                              key={i}
                              className="flex items-start gap-2 rounded-lg bg-amber-500/5 border border-amber-500/10 px-3 py-2 text-xs text-foreground"
                            >
                              <Shield className="h-3.5 w-3.5 text-amber-500 shrink-0 mt-0.5" />
                              {flag}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Recommendations */}
                    {result.recommendations.length > 0 && (
                      <div>
                        <div className="flex items-center gap-2 mb-2.5">
                          <CheckCircle2 className="h-4 w-4 text-emerald-500" />
                          <h3 className="text-sm font-semibold">
                            Recommendations
                          </h3>
                        </div>
                        <ul className="space-y-1.5 pl-1">
                          {result.recommendations.map((rec, i) => (
                            <li
                              key={i}
                              className="flex items-start gap-2 text-xs text-muted-foreground leading-relaxed"
                            >
                              <span className="text-primary mt-0.5">•</span>
                              {rec}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* What to do next — ordered, because these are steps. */}
                    {result.action_steps.length > 0 && (
                      <div>
                        <div className="flex items-center gap-2 mb-2.5">
                          <ListChecks className="h-4 w-4 text-primary" />
                          <h3 className="text-sm font-semibold">What to do next</h3>
                        </div>
                        <ol className="space-y-2">
                          {result.action_steps.map((step, i) => (
                            <li key={i} className="flex items-start gap-2.5 text-xs leading-relaxed">
                              <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-primary/10 text-[10px] font-semibold tabular-nums text-primary">
                                {i + 1}
                              </span>
                              <span className="text-muted-foreground pt-0.5">{step}</span>
                            </li>
                          ))}
                        </ol>
                      </div>
                    )}

                    {/* Citations. These come from the statute corpus rather
                        than the model, so every one resolves to real text the
                        reader can open and check. */}
                    {result.sources.length > 0 && (
                      <div className="border-t border-border/50 pt-4">
                        <div className="flex items-center gap-2 mb-2.5">
                          <Library className="h-4 w-4 text-muted-foreground" />
                          <h3 className="text-sm font-semibold">Law referred to</h3>
                        </div>
                        <ul className="space-y-1.5">
                          {result.sources.map((source, i) => (
                            <li key={i} className="text-xs leading-relaxed">
                              <a
                                href={source.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-primary hover:underline underline-offset-2"
                              >
                                {source.citation}
                              </a>
                              <span className="text-muted-foreground/70"> — {source.title}</span>
                            </li>
                          ))}
                        </ul>
                        <p className="mt-3 text-[11px] leading-relaxed text-muted-foreground/70">
                          This is legal information, not legal advice. For advice on your
                          situation, free legal aid is available on 15100.
                        </p>
                      </div>
                    )}
                  </div>
                ) : (
                  /* ── Empty state ── */
                  <div className="flex h-full flex-col items-center justify-center text-center text-muted-foreground">
                    <div className="relative mb-5">
                      <div className="rounded-2xl bg-gradient-to-br from-primary/10 to-primary/5 p-5 shadow-sm">
                        <Scale className="h-10 w-10 text-primary/40" />
                      </div>
                      <div className="absolute -top-1 -right-1 flex h-5 w-5 items-center justify-center rounded-full bg-muted text-muted-foreground/50">
                        <Sparkles className="h-3 w-3" />
                      </div>
                    </div>
                    <h3 className="text-sm font-semibold text-foreground mb-1.5">
                      No Output Yet
                    </h3>
                    <p className="text-xs max-w-[240px] leading-relaxed text-muted-foreground/80">
                      Upload a document or paste text, then click
                      &lsquo;Process Document&rsquo; to begin analysis.
                    </p>
                    <div className="flex flex-wrap justify-center gap-1.5 mt-6">
                      {["Clause Extraction", "Risk Analysis", "Summarization"].map(
                        (feature) => (
                          <span
                            key={feature}
                            className="rounded-full bg-muted/60 px-2.5 py-1 text-[10px] font-medium text-muted-foreground/70 tracking-wide"
                          >
                            {feature}
                          </span>
                        )
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
