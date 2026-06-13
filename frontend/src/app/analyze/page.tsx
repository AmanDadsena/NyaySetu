"use client";

import { useState, useRef, useCallback } from "react";
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
} from "lucide-react";

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
  const [isProcessing, setIsProcessing] = useState(false);
  const [text, setText] = useState("");
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [language, setLanguage] = useState("English");
  const fileInputRef = useRef<HTMLInputElement>(null);

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

  // ── Process document ───────────────────────────────────────────────────
  const handleProcess = async () => {
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
      formData.append("language", language);

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
    } catch (err) {
      const message = err instanceof Error ? err.message : "An unexpected error occurred";
      setError(message);
    } finally {
      setIsProcessing(false);
    }
  };

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
                <p className="text-xs text-muted-foreground/70 hidden sm:block">
                  Supports contracts, judgments, statutes & more
                </p>
                <div className="flex items-center gap-3 w-full sm:w-auto">
                  <Select value={language} onValueChange={setLanguage} disabled={isProcessing}>
                    <SelectTrigger className="w-[140px] h-10 rounded-full bg-background/50 border-border/50">
                      <SelectValue placeholder="Language" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="English">English</SelectItem>
                      <SelectItem value="Hindi">Hindi</SelectItem>
                      <SelectItem value="Marathi">Marathi</SelectItem>
                      <SelectItem value="Gujarati">Gujarati</SelectItem>
                      <SelectItem value="Tamil">Tamil</SelectItem>
                      <SelectItem value="Telugu">Telugu</SelectItem>
                      <SelectItem value="Bengali">Bengali</SelectItem>
                      <SelectItem value="Kannada">Kannada</SelectItem>
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
                        Processing…
                      </>
                    ) : (
                      <>
                        <Play className="mr-2 h-4 w-4" />
                        Process Document
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
                    {/* Summary card */}
                    <div className="rounded-xl bg-gradient-to-br from-primary/5 to-primary/[0.02] border border-primary/10 p-4">
                      <div className="flex items-center gap-2 mb-2">
                        <BookOpen className="h-4 w-4 text-primary" />
                        <h3 className="text-sm font-semibold">Summary</h3>
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
