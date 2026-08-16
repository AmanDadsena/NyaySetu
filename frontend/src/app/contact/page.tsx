import type { Metadata } from "next";
// lucide v1 dropped its brand icons, so `Code2` stands in for the GitHub mark.
import { Bug, Code2, MessageSquareWarning, Phone } from "lucide-react";
import { LegalShell, Section, Note } from "@/components/LegalShell";

export const metadata: Metadata = {
  title: "Contact — Nyaysetu",
  description:
    "How to report a wrong answer, file a bug, or reach the helplines that can actually help with a legal emergency.",
};

const REPO = "https://github.com/AmanDadsena/Nyaysetu";

/**
 * Public helplines, all free to call from anywhere in India.
 *
 * These are on the contact page rather than buried, because a person who has
 * navigated to "Contact" during a legal emergency needs a number that answers,
 * not a form that gets read next week. Nyaysetu is not that number.
 */
const HELPLINES = [
  {
    number: "112",
    name: "Emergency",
    detail: "Police, fire and ambulance. The single national emergency number.",
  },
  {
    number: "15100",
    name: "Free legal aid (NALSA)",
    detail:
      "Legal advice and representation at no cost, a statutory right for most people in India.",
  },
  {
    number: "181",
    name: "Women's helpline",
    detail: "Support and assistance for women facing violence or harassment.",
  },
  {
    number: "1098",
    name: "Childline",
    detail: "For children in need of care and protection.",
  },
  {
    number: "1930",
    name: "Cyber crime",
    detail:
      "Report online financial fraud. Call quickly — the first hours matter most for recovering money.",
  },
  {
    number: "14567",
    name: "Elderline",
    detail: "Support for senior citizens, including on maintenance and abuse.",
  },
] as const;

export default function ContactPage() {
  return (
    <LegalShell
      title="Contact"
      lede="This is a small open-source project, not a company with a support desk. Here is what will actually get a response — and what to call if the matter cannot wait."
      updated="16 August 2026"
    >
      <Section heading="If you need help now, call — do not write">
        <Note tone="warn">
          Nyaysetu is not monitored in real time and cannot help in an
          emergency. The numbers below are free, staffed, and reachable from any
          phone in India.
        </Note>
        <div className="mt-5 grid gap-3 sm:grid-cols-2">
          {HELPLINES.map((line) => (
            <a
              key={line.number}
              href={`tel:${line.number}`}
              className="lift group flex gap-4 rounded-2xl border border-gray-200 bg-white p-5 hover:border-amber-300 hover:shadow-md"
            >
              <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-amber-50 text-amber-700 transition-colors group-hover:bg-amber-100">
                <Phone className="h-5 w-5" aria-hidden="true" />
              </span>
              <span className="min-w-0">
                <span className="block font-mono text-lg font-bold tracking-tight text-slate-900">
                  {line.number}
                </span>
                <span className="block text-sm font-medium text-slate-700">
                  {line.name}
                </span>
                <span className="mt-1 block text-xs leading-relaxed text-gray-500">
                  {line.detail}
                </span>
              </span>
            </a>
          ))}
        </div>
      </Section>

      <Section heading="Reporting a wrong answer">
        <p>
          This is the most useful thing you can send. If the assistant cited the
          wrong provision, missed an obvious one, or answered a question it
          should have declined, open an issue with the question you asked and
          the language you asked it in. Retrieval failures are reproducible, and
          a reported one usually becomes a test case.
        </p>
        <a
          href={`${REPO}/issues/new`}
          target="_blank"
          rel="noopener noreferrer"
          className="lift mt-2 inline-flex items-center gap-2.5 rounded-full bg-slate-900 px-6 py-3 text-sm font-medium text-white hover:bg-slate-800"
        >
          <MessageSquareWarning className="h-4 w-4" aria-hidden="true" />
          Report a wrong answer
        </a>
      </Section>

      <Section heading="Bugs, features and code">
        <p>
          Everything about this project is public — the corpus, the retrieval
          code, the evaluation that gates changes to it, and the issue tracker.
          Bug reports and pull requests are welcome through the repository.
        </p>
        <div className="flex flex-wrap gap-3 pt-1">
          <a
            href={REPO}
            target="_blank"
            rel="noopener noreferrer"
            className="lift inline-flex items-center gap-2.5 rounded-full border border-gray-200 bg-white px-6 py-3 text-sm font-medium text-slate-900 hover:border-slate-300"
          >
            <Code2 className="h-4 w-4" aria-hidden="true" />
            Source repository
          </a>
          <a
            href={`${REPO}/issues`}
            target="_blank"
            rel="noopener noreferrer"
            className="lift inline-flex items-center gap-2.5 rounded-full border border-gray-200 bg-white px-6 py-3 text-sm font-medium text-slate-900 hover:border-slate-300"
          >
            <Bug className="h-4 w-4" aria-hidden="true" />
            Open issues
          </a>
        </div>
      </Section>

      <Section heading="What this project cannot do for you">
        <p>
          It cannot take your case, recommend a particular advocate, review a
          document you send, or tell you what a court will decide. Those all
          require an advocate who has heard your facts and is accountable for
          the answer. If cost is the obstacle, 15100 exists precisely for that.
        </p>
      </Section>
    </LegalShell>
  );
}
