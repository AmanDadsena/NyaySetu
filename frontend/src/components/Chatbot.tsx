"use client";

import React, { useCallback, useEffect, useRef, useState } from "react";
import {
  MessageCircle,
  X,
  Send,
  Bot,
  User,
  Sparkles,
  Scale,
  Volume2,
  VolumeX,
} from "lucide-react";
import { VoiceButton } from "@/components/VoiceButton";
import { useLanguage } from "@/lib/i18n/LanguageProvider";
import type { TranslationKey } from "@/lib/i18n/translations";
import { useSpeechSynthesis } from "@/lib/voice/useSpeechSynthesis";

/**
 * Suggested questions, paired with the id of the statute passage that answers
 * them. Pinning retrieval by id means a chip tapped in Tamil lands on exactly
 * the right provision — the corpus is written in English, so matching the
 * translated chip text would be luck at best.
 *
 * Ids must exist in backend/app/rag/corpus.py.
 */
const FAQ_CHIPS: { key: TranslationKey; topic: string }[] = [
  { key: "bot.faq1", topic: "legal_aid_eligibility" },
  { key: "bot.faq2", topic: "fir_how_to_file" },
  { key: "bot.faq3", topic: "arrest_rights" },
  { key: "bot.faq4", topic: "consumer_where_to_file" },
  { key: "bot.faq5", topic: "bns_overview" },
];

interface SourceRef {
  title: string;
  citation: string;
  url: string;
}

/** Events emitted by /api/bot/chat/stream. */
type StreamEvent =
  | { type: "sources"; sources: SourceRef[]; grounding: string }
  | { type: "delta"; text: string }
  | { type: "done"; provider: string; grounding?: string };

type Role = "user" | "model";

interface Message {
  role: Role;
  content: string;
  /** Statute passages the answer was grounded in. Model turns only. */
  sources?: SourceRef[];
}

export function Chatbot() {
  const { t, meta } = useLanguage();

  const [isOpen, setIsOpen] = useState(false);
  // Holds the conversation only. The greeting is rendered from the active
  // translation instead of being stored, so switching language re-greets the
  // user in the new language rather than stranding an English bubble.
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [voiceNotice, setVoiceNotice] = useState<string | null>(null);
  /** Index in `messages` currently being read aloud, or null. */
  const [speakingIndex, setSpeakingIndex] = useState<number | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  /** True when the pending question arrived by voice, so the reply is spoken. */
  const spokenQuestionRef = useRef(false);

  const { isSpeaking, speak, stop: stopSpeaking } = useSpeechSynthesis({
    lang: meta.speech,
  });

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, isOpen, isLoading]);

  // Focus the input when the window opens
  useEffect(() => {
    if (isOpen && inputRef.current) {
      setTimeout(() => inputRef.current?.focus(), 350);
    }
  }, [isOpen]);

  // Clear the speaking highlight once synthesis finishes on its own.
  useEffect(() => {
    if (!isSpeaking) setSpeakingIndex(null);
  }, [isSpeaking]);

  // Stop any read-aloud when the panel is closed.
  useEffect(() => {
    if (!isOpen) stopSpeaking();
  }, [isOpen, stopSpeaking]);

  const toggleSpeak = useCallback(
    (index: number, text: string) => {
      if (speakingIndex === index && isSpeaking) {
        stopSpeaking();
        setSpeakingIndex(null);
      } else {
        setSpeakingIndex(index);
        speak(text);
      }
    },
    [speakingIndex, isSpeaking, speak, stopSpeaking],
  );

  const sendMessage = useCallback(
    async (text: string, opts: { fromVoice?: boolean; topic?: string } = {}) => {
      const { fromVoice = false, topic } = opts;
      if (!text.trim()) return;

      spokenQuestionRef.current = fromVoice;
      setVoiceNotice(null);

      const history = messages;
      setMessages((prev) => [...prev, { role: "user", content: text }]);
      setInput("");
      setIsLoading(true);

      // Index the streaming reply will occupy: the history, plus the user turn
      // just appended.
      const replyIndex = history.length + 1;

      try {
        const res = await fetch(
          (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000") + "/api/bot/chat/stream",
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              message: text,
              history,
              language: meta.gemini,
              topic,
            }),
          },
        );

        if (!res.ok || !res.body) throw new Error("Failed to communicate with bot");

        // Create the empty model bubble up front so text can flow into it.
        setMessages((prev) => [...prev, { role: "model", content: "", sources: [] }]);
        setIsLoading(false);

        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";
        let full = "";

        const applyEvent = (event: StreamEvent) => {
          if (event.type === "sources") {
            setMessages((prev) =>
              prev.map((m, i) => (i === replyIndex ? { ...m, sources: event.sources } : m)),
            );
          } else if (event.type === "delta") {
            full += event.text;
            setMessages((prev) =>
              prev.map((m, i) => (i === replyIndex ? { ...m, content: full } : m)),
            );
          }
        };

        // Read until the stream closes, splitting on the SSE record separator.
        // A chunk can end mid-record, so the tail stays in the buffer.
        for (;;) {
          const { done, value } = await reader.read();
          if (done) break;
          buffer += decoder.decode(value, { stream: true });

          const records = buffer.split("\n\n");
          buffer = records.pop() ?? "";
          for (const record of records) {
            const line = record.trim();
            if (!line.startsWith("data:")) continue;
            try {
              applyEvent(JSON.parse(line.slice(5).trim()) as StreamEvent);
            } catch {
              // Ignore a malformed record rather than killing the stream.
            }
          }
        }

        if (!full.trim()) throw new Error("Empty response");

        // A question asked by voice gets its answer read back, closing the loop
        // for someone who can't comfortably read the screen. Speak only once
        // the full text has arrived, so the voice isn't chasing the stream.
        if (spokenQuestionRef.current) {
          setSpeakingIndex(replyIndex);
          speak(full);
        }
      } catch (error) {
        console.error(error);
        setMessages((prev) => {
          const next = [...prev];
          // Replace the empty streaming bubble if one was created.
          if (next[replyIndex]?.role === "model" && !next[replyIndex].content) {
            next[replyIndex] = { role: "model", content: t("bot.error") };
            return next;
          }
          return [...next, { role: "model", content: t("bot.error") }];
        });
      } finally {
        setIsLoading(false);
        spokenQuestionRef.current = false;
      }
    },
    [messages, meta.gemini, speak, t],
  );

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage(input);
    }
  };

  /** Renders markdown-bold (**…**) as <strong> tags and handles line breaks */
  const renderContent = (text: string) => {
    // Split by newlines first
    const lines = text.split("\n");
    return lines.map((line, lineIdx) => {
      // Render bold within each line
      const parts = line.split(/(\*\*[^*]+\*\*)/g);
      const rendered = parts.map((p, i) => {
        if (p.startsWith("**") && p.endsWith("**")) {
          return <strong key={i}>{p.slice(2, -2)}</strong>;
        }
        return <span key={i}>{p}</span>;
      });
      return (
        <span key={lineIdx}>
          {rendered}
          {lineIdx < lines.length - 1 && <br />}
        </span>
      );
    });
  };

  const greeting = t("bot.greeting");

  return (
    <div className="fixed bottom-5 right-5 z-50" id="chatbot-root">
      {/* ── Chat Window ─────────────────────────────────────────── */}
      <div
        className={`absolute bottom-[76px] right-0 w-[400px] chatbot-window ${
          isOpen ? "chatbot-window-open" : "chatbot-window-closed"
        }`}
        style={{ pointerEvents: isOpen ? "auto" : "none" }}
      >
        <div className="chatbot-glass flex flex-col h-[580px] rounded-3xl overflow-hidden">
          {/* ── Header ────────────────────────────────────────── */}
          <div className="chatbot-header relative px-5 py-4 flex items-center justify-between">
            {/* Animated gradient overlay */}
            <div className="absolute inset-0 chatbot-header-gradient" />

            <div className="relative z-10 flex items-center gap-3">
              {/* Breathing orb */}
              <div className="chatbot-orb">
                <Scale className="w-5 h-5 text-white drop-shadow-lg" />
              </div>
              <div>
                <h3 className="font-bold text-[15px] text-white tracking-tight leading-tight">
                  {t("bot.title")}
                </h3>
                <p className="text-[11px] text-white/70 font-medium flex items-center gap-1">
                  <span className="inline-block w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  {t("bot.status")}
                </p>
              </div>
            </div>

            <button
              onClick={() => setIsOpen(false)}
              className="relative z-10 p-1.5 rounded-full hover:bg-white/15 transition-colors"
              aria-label={t("bot.close")}
            >
              <X className="w-4 h-4 text-white/90" />
            </button>
          </div>

          {/* ── Messages ──────────────────────────────────────── */}
          <div className="flex-1 overflow-y-auto chatbot-messages px-4 py-4 space-y-3">
            {/* Greeting — reactive to the active language */}
            <div className="chatbot-msg flex gap-2.5 justify-start">
              <div className="chatbot-avatar-bot shrink-0">
                <Sparkles className="w-3.5 h-3.5" />
              </div>
              <div className="chatbot-bubble chatbot-bubble-bot">
                <div className="whitespace-pre-wrap leading-relaxed">
                  {renderContent(greeting)}
                </div>
              </div>
            </div>

            {messages.map((msg, i) => (
              <div
                key={i}
                className={`chatbot-msg flex gap-2.5 ${
                  msg.role === "user" ? "justify-end" : "justify-start"
                }`}
                style={{ animationDelay: `${Math.min(i * 0.06, 0.4)}s` }}
              >
                {msg.role === "model" && (
                  <div className="chatbot-avatar-bot shrink-0">
                    <Sparkles className="w-3.5 h-3.5" />
                  </div>
                )}
                <div
                  className={`chatbot-bubble ${
                    msg.role === "user" ? "chatbot-bubble-user" : "chatbot-bubble-bot"
                  }`}
                >
                  <div className="whitespace-pre-wrap leading-relaxed">
                    {renderContent(msg.content)}
                  </div>
                  {/* Citations. A legal answer the reader cannot verify is
                      worth less than one they can, so the statute behind it is
                      always shown and always linkable. */}
                  {msg.role === "model" && msg.sources && msg.sources.length > 0 && (
                    <div className="chatbot-sources">
                      <p className="chatbot-sources-label">
                        {t("bot.basedOn")}
                      </p>
                      <ul>
                        {msg.sources.map((source, s) => (
                          <li key={s}>
                            <a href={source.url} target="_blank" rel="noopener noreferrer">
                              {source.citation}
                            </a>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {msg.role === "model" && (
                    <button
                      type="button"
                      onClick={() => toggleSpeak(i, msg.content)}
                      aria-label={
                        speakingIndex === i && isSpeaking
                          ? t("voice.stopReading")
                          : t("voice.readAloud")
                      }
                      title={
                        speakingIndex === i && isSpeaking
                          ? t("voice.stopReading")
                          : t("voice.readAloud")
                      }
                      aria-pressed={speakingIndex === i && isSpeaking}
                      className="mt-2 inline-flex items-center gap-1 rounded-full px-2 py-1 text-[11px] font-medium text-gray-500 transition-colors hover:bg-gray-100 hover:text-gray-800"
                    >
                      {speakingIndex === i && isSpeaking ? (
                        <>
                          <VolumeX className="w-3 h-3" />
                          {t("voice.stopReading")}
                        </>
                      ) : (
                        <>
                          <Volume2 className="w-3 h-3" />
                          {t("voice.readAloud")}
                        </>
                      )}
                    </button>
                  )}
                </div>
                {msg.role === "user" && (
                  <div className="chatbot-avatar-user shrink-0">
                    <User className="w-3.5 h-3.5" />
                  </div>
                )}
              </div>
            ))}

            {/* ── FAQ Chips ── */}
            {messages.length === 0 && (
              <div className="flex flex-col gap-2 pt-2">
                <p className="text-[11px] font-semibold uppercase tracking-wider text-gray-400 px-1">
                  {t("bot.popularQuestions")}
                </p>
                {FAQ_CHIPS.map(({ key, topic }, i) => (
                  <button
                    key={key}
                    onClick={() => sendMessage(t(key), { topic })}
                    className="chatbot-faq-chip"
                    style={{ animationDelay: `${0.5 + i * 0.08}s` }}
                  >
                    <span className="text-primary/70 mr-1.5">→</span>
                    {t(key)}
                  </button>
                ))}
              </div>
            )}

            {/* ── Typing indicator ── */}
            {isLoading && (
              <div className="chatbot-msg flex gap-2.5 justify-start">
                <div className="chatbot-avatar-bot shrink-0">
                  <Bot className="w-3.5 h-3.5" />
                </div>
                <div className="chatbot-bubble chatbot-bubble-bot flex items-center gap-2">
                  <div className="chatbot-typing-dots">
                    <span />
                    <span />
                    <span />
                  </div>
                  <span className="text-[11px] text-gray-400 font-medium">
                    {t("bot.thinking")}
                  </span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* ── Input Area ─────────────────────────────────────── */}
          <div className="chatbot-input-bar">
            {voiceNotice && (
              <p className="mb-2 rounded-lg bg-amber-50 px-2.5 py-1.5 text-[11px] text-amber-800">
                {voiceNotice}
              </p>
            )}
            <div className="relative flex items-center gap-2">
              <VoiceButton
                onTranscript={(text) => sendMessage(text, { fromVoice: true })}
                onError={setVoiceNotice}
                disabled={isLoading}
              />
              <div className="relative flex flex-1 items-center">
                <input
                  ref={inputRef}
                  type="text"
                  placeholder={t("bot.placeholder")}
                  className="chatbot-input"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  disabled={isLoading}
                />
                <button
                  onClick={() => sendMessage(input)}
                  disabled={!input.trim() || isLoading}
                  className="chatbot-send-btn"
                  aria-label={t("bot.send")}
                >
                  <Send className="w-4 h-4" />
                </button>
              </div>
            </div>
            <p className="text-[10px] text-center text-gray-400 mt-2 select-none">
              {t("bot.disclaimer")}
            </p>
          </div>
        </div>
      </div>

      {/* ── Floating Action Button ──────────────────────────────── */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`chatbot-fab ${isOpen ? "chatbot-fab-active" : ""}`}
        aria-label={isOpen ? t("bot.close") : t("bot.open")}
      >
        {/* Pulse ring */}
        {!isOpen && <span className="chatbot-fab-ring" />}
        <span className="chatbot-fab-icon">
          {isOpen ? (
            <X className="w-6 h-6" />
          ) : (
            <MessageCircle className="w-6 h-6" />
          )}
        </span>
      </button>
    </div>
  );
}
