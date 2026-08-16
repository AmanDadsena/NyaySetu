"use client";

/**
 * A live-looking demonstration of what the assistant actually does.
 *
 * This replaced a hero video hotlinked from a CloudFront URL — an expiring
 * dependency showing generic footage that demonstrated nothing about the
 * product. What is shown here instead is the real behaviour: a question, a
 * short answer, and the provision the answer rests on.
 *
 * **Every question, answer and citation below is drawn from the actual
 * corpus.** The act names and section numbers are the ones the retriever would
 * return for these questions, taken from `backend/app/rag/corpus.py`. A demo
 * that invented a plausible-looking citation would be the exact failure this
 * whole project is built to avoid — the README's phrase for it is that the
 * extractive path "cannot invent a section number because it never writes one",
 * and a marketing component should be held to the same standard.
 */

import { useEffect, useRef, useState } from "react";
import { ArrowUpRight, BookOpen, Sparkles } from "lucide-react";

interface Example {
  /** Corpus passage id this is drawn from, for anyone checking. */
  id: string;
  question: string;
  answer: string;
  act: string;
  section: string;
  url: string;
}

const EXAMPLES: Example[] = [
  {
    id: "legal_aid_eligibility",
    question: "Can I get a lawyer if I can't afford one?",
    answer:
      "Yes — free legal aid is a statutory right, not charity. Every woman and every child qualifies, as does any member of a Scheduled Caste or Scheduled Tribe, any person with a disability, any person in custody, and anyone whose annual income is below the limit their State sets.",
    act: "Legal Services Authorities Act, 1987",
    section: "Section 12",
    url: "https://nalsa.gov.in",
  },
  {
    id: "fir_refusal_remedy",
    question: "The police refused to file my FIR. What now?",
    answer:
      "You have an escalating set of remedies. Send the complaint in writing by registered post to the Superintendent of Police, who must investigate if it discloses a cognizable offence. If that fails too, apply to the Judicial Magistrate, who can direct the police to investigate.",
    act: "Bharatiya Nagarik Suraksha Sanhita, 2023",
    section: "Sections 173(4) and 175(3)",
    url: "https://www.indiacode.nic.in",
  },
  {
    id: "arrest_rights",
    question: "What are my rights if I am arrested?",
    answer:
      "You must be told the grounds of your arrest. You have the right to consult and be defended by a lawyer of your choice, and to free legal aid if you cannot afford one. You must be produced before a Magistrate within twenty-four hours, excluding travel time.",
    act: "Constitution of India and Bharatiya Nagarik Suraksha Sanhita, 2023",
    section: "Articles 20–22; BNSS Sections 47 and 58",
    url: "https://www.indiacode.nic.in",
  },
];

const THINK_MS = 850;
const TYPE_MS = 16;
const REST_MS = 4200;

type Phase = "thinking" | "typing" | "rest";

export function AnswerPreview() {
  const [index, setIndex] = useState(0);
  const [phase, setPhase] = useState<Phase>("thinking");
  const [chars, setChars] = useState(0);
  // When motion is reduced the whole thing renders as a finished answer.
  const [animate, setAnimate] = useState(true);

  const example = EXAMPLES[index];
  const timers = useRef<ReturnType<typeof setTimeout>[]>([]);

  useEffect(() => {
    const reduced =
      typeof window.matchMedia === "function" &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduced) {
      setAnimate(false);
      setPhase("rest");
      setChars(EXAMPLES[0].answer.length);
    }
  }, []);

  useEffect(() => {
    if (!animate) return;

    const clearAll = () => {
      timers.current.forEach(clearTimeout);
      timers.current = [];
    };

    setPhase("thinking");
    setChars(0);

    timers.current.push(
      setTimeout(() => {
        setPhase("typing");

        const total = example.answer.length;
        // Type in small chunks rather than per character: one setState every
        // 16ms for 280 characters is a lot of renders for no visible gain.
        let shown = 0;
        const step = () => {
          shown = Math.min(shown + 3, total);
          setChars(shown);
          if (shown < total) {
            timers.current.push(setTimeout(step, TYPE_MS));
          } else {
            setPhase("rest");
            timers.current.push(
              setTimeout(() => setIndex((i) => (i + 1) % EXAMPLES.length), REST_MS),
            );
          }
        };
        step();
      }, THINK_MS),
    );

    return clearAll;
  }, [index, animate, example.answer]);

  const revealed = example.answer.slice(0, chars);
  const showCitation = phase === "rest";

  return (
    <div className="relative mx-auto w-full max-w-2xl">
      {/* Soft glow behind the card so it sits above the hero rather than on it. */}
      <div
        aria-hidden="true"
        className="animate-aurora pointer-events-none absolute -inset-8 rounded-[3rem] bg-gradient-to-tr from-amber-200/40 via-purple-200/30 to-sky-200/40 blur-3xl"
      />

      <div className="relative overflow-hidden rounded-3xl border border-white/60 bg-white/90 shadow-2xl shadow-slate-900/10 backdrop-blur-xl">
        {/* Header */}
        <div className="chatbot-header relative flex items-center gap-3 px-5 py-4">
          <div className="chatbot-header-gradient" aria-hidden="true" />
          <div className="chatbot-orb relative z-10">
            <Sparkles className="h-4 w-4 text-white" aria-hidden="true" />
          </div>
          <div className="relative z-10">
            <p className="text-sm font-semibold text-white">Nyaysetu Guide</p>
            <p className="text-[11px] text-white/70">
              Answers from cited statute, in eight languages
            </p>
          </div>
        </div>

        {/* Conversation */}
        <div className="chatbot-messages space-y-4 px-5 py-6 min-h-[21rem]">
          {/* Question */}
          <div key={`q-${index}`} className="chatbot-msg flex justify-end">
            <p className="chatbot-bubble chatbot-bubble-user">{example.question}</p>
          </div>

          {/* Answer */}
          <div key={`a-${index}`} className="chatbot-msg flex gap-2.5">
            <span className="chatbot-avatar-bot" aria-hidden="true">
              <BookOpen className="h-3.5 w-3.5" />
            </span>

            <div className="chatbot-bubble chatbot-bubble-bot">
              {phase === "thinking" ? (
                <span className="chatbot-typing-dots" aria-label="Thinking">
                  <span />
                  <span />
                  <span />
                </span>
              ) : (
                <>
                  <span>{revealed}</span>
                  {phase === "typing" && (
                    <span className="animate-caret ml-0.5 inline-block h-3.5 w-[2px] translate-y-0.5 bg-slate-400" />
                  )}

                  {/* The citation is the point. It arrives after the answer,
                      the way it does in the real chatbot. */}
                  {showCitation && (
                    <span className="chatbot-sources">
                      <span className="chatbot-sources-label">Based on</span>
                      <ul>
                        <li>
                          <a
                            href={example.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-start gap-1"
                          >
                            <span>
                              {example.act} — {example.section}
                            </span>
                            <ArrowUpRight
                              className="mt-0.5 h-3 w-3 shrink-0 opacity-70"
                              aria-hidden="true"
                            />
                          </a>
                        </li>
                      </ul>
                    </span>
                  )}
                </>
              )}
            </div>
          </div>
        </div>

        {/* Which example is showing */}
        <div className="flex items-center justify-between border-t border-gray-100 bg-white/70 px-5 py-3">
          <p className="text-[11px] text-gray-400">
            Real questions, real citations — nothing here is mocked up
          </p>
          <div className="flex gap-1.5">
            {EXAMPLES.map((ex, i) => (
              <button
                key={ex.id}
                type="button"
                onClick={() => setIndex(i)}
                aria-label={`Show example ${i + 1}: ${ex.question}`}
                aria-current={i === index}
                className={
                  i === index
                    ? "h-1.5 w-6 rounded-full bg-slate-800 transition-all"
                    : "h-1.5 w-1.5 rounded-full bg-gray-300 transition-all hover:bg-gray-400"
                }
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
