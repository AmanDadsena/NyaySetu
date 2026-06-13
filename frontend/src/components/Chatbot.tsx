"use client";

import React, { useState, useRef, useEffect } from "react";
import {
  MessageCircle,
  X,
  Send,
  Bot,
  User,
  Sparkles,
  Scale,
} from "lucide-react";

const POPULAR_FAQS = [
  "How can I get free legal aid in India (NALSA)?",
  "What is the process to file an FIR?",
  "What are my basic rights if arrested?",
  "How do I file a consumer court complaint?",
  "What are the key changes in Bharatiya Nyaya Sanhita?",
];

type Role = "user" | "model";

interface Message {
  role: Role;
  content: string;
}

export function Chatbot() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "model",
      content:
        "Namaste! 🙏 I'm your **Nyaysetu** legal guide. Ask me anything about Indian law, your rights, or legal procedures — or pick a question below to get started.",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, isOpen]);

  // Focus the input when the window opens
  useEffect(() => {
    if (isOpen && inputRef.current) {
      setTimeout(() => inputRef.current?.focus(), 350);
    }
  }, [isOpen]);

  const sendMessage = async (text: string) => {
    if (!text.trim()) return;

    const userMsg: Message = { role: "user", content: text };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsLoading(true);

    try {
      const history = messages.filter((_, i) => i > 0);

      const res = await fetch((process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000") + "/api/bot/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text, history }),
      });

      if (!res.ok) throw new Error("Failed to communicate with bot");

      const data = await res.json();
      setMessages((prev) => [...prev, { role: "model", content: data.reply }]);
    } catch (error) {
      console.error(error);
      setMessages((prev) => [
        ...prev,
        {
          role: "model",
          content:
            "Sorry, I'm having trouble connecting right now. Please try again later.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

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
                  Nyaysetu Guide
                </h3>
                <p className="text-[11px] text-white/70 font-medium flex items-center gap-1">
                  <span className="inline-block w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  AI Legal Assistant · Online
                </p>
              </div>
            </div>

            <button
              onClick={() => setIsOpen(false)}
              className="relative z-10 p-1.5 rounded-full hover:bg-white/15 transition-colors"
              aria-label="Close chat"
            >
              <X className="w-4 h-4 text-white/90" />
            </button>
          </div>

          {/* ── Messages ──────────────────────────────────────── */}
          <div className="flex-1 overflow-y-auto chatbot-messages px-4 py-4 space-y-3">
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
                </div>
                {msg.role === "user" && (
                  <div className="chatbot-avatar-user shrink-0">
                    <User className="w-3.5 h-3.5" />
                  </div>
                )}
              </div>
            ))}

            {/* ── FAQ Chips ── */}
            {messages.length === 1 && (
              <div className="flex flex-col gap-2 pt-2">
                <p className="text-[11px] font-semibold uppercase tracking-wider text-gray-400 px-1">
                  Popular Questions
                </p>
                {POPULAR_FAQS.map((faq, i) => (
                  <button
                    key={i}
                    onClick={() => sendMessage(faq)}
                    className="chatbot-faq-chip"
                    style={{ animationDelay: `${0.5 + i * 0.08}s` }}
                  >
                    <span className="text-primary/70 mr-1.5">→</span>
                    {faq}
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
                    Thinking…
                  </span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* ── Input Area ─────────────────────────────────────── */}
          <div className="chatbot-input-bar">
            <div className="relative flex items-center">
              <input
                ref={inputRef}
                type="text"
                placeholder="Ask a legal question…"
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
                aria-label="Send message"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
            <p className="text-[10px] text-center text-gray-400 mt-2 select-none">
              Nyaysetu AI may make mistakes · Verify important legal info
            </p>
          </div>
        </div>
      </div>

      {/* ── Floating Action Button ──────────────────────────────── */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`chatbot-fab ${isOpen ? "chatbot-fab-active" : ""}`}
        aria-label="Toggle chatbot"
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
