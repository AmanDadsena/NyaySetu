import type { Metadata } from "next";
import Link from "next/link";
import { LegalShell, Section, Note, Bullets } from "@/components/LegalShell";
import { KNOWN_GAPS, LEGAL_AID_HELPLINE } from "@/lib/site-stats";

export const metadata: Metadata = {
  title: "Disclaimer — Nyaysetu",
  description:
    "Nyaysetu gives legal information, not legal advice. What that distinction means, and where this tool is known to be wrong.",
};

export default function DisclaimerPage() {
  return (
    <LegalShell
      title="Disclaimer"
      lede="Nyaysetu provides legal information, not legal advice. That distinction is not a formality — it changes what you should do with what you read here."
      updated="16 August 2026"
    >
      <Section heading="Information, not advice">
        <p>
          Legal <em>information</em> is a statement of what the law says. Legal{" "}
          <em>advice</em> is a judgement about what you specifically should do,
          made by someone who has heard your facts, is qualified to weigh them,
          and is accountable if they get it wrong. This application does the
          first. It cannot do the second.
        </p>
        <p>
          Every answer the assistant gives cites the provision it rests on,
          precisely so you can check it against the source rather than take this
          tool&rsquo;s word for it. If an answer does not show you a provision,
          treat it as unverified.
        </p>
      </Section>

      <Section heading="No advocate–client relationship">
        <p>
          Using this site does not create an advocate–client relationship with
          anyone. Nothing you type here is privileged. Messages sent through the
          case board are stored in plain text and can be read by whoever
          operates the service — see the{" "}
          <Link href="/privacy" className="font-medium text-amber-700 underline underline-offset-2 hover:text-amber-800">
            privacy page
          </Link>
          .
        </p>
      </Section>

      <Section heading="Where this tool is known to fall short">
        <p>
          Published rather than buried. These come from the project&rsquo;s own
          evaluation, which runs on every change to the corpus or the retriever.
        </p>
        <div className="space-y-4">
          {KNOWN_GAPS.map((item) => (
            <div
              key={item.gap}
              className="rounded-2xl border border-gray-200 bg-gray-50/70 p-5"
            >
              <h3 className="mb-2 font-semibold text-slate-900">{item.gap}</h3>
              <p className="text-[15px] leading-relaxed text-gray-600">
                {item.detail}
              </p>
            </div>
          ))}
        </div>
      </Section>

      <Section heading="The law changes; this corpus is a snapshot">
        <p>
          Statutes are amended, sections are renumbered, and judgments reinterpret
          settled positions. The corpus here is curated and dated, not a live
          feed from a government gazette. For anything where currency matters —
          and for limitation periods it almost always does — confirm against the
          official source before you rely on it.
        </p>
        <Bullets
          items={[
            "Deadlines the toolkit computes are calendar arithmetic over a stated rule. They do not account for facts a court might treat as extending or excusing delay.",
            "Court fees and stamp duty vary by State and are revised. The figures here are a starting estimate, not a receipt.",
            "Document templates are drafting aids. A court can reject a filing for reasons no template anticipates.",
          ]}
        />
      </Section>

      <Section heading="If your matter is serious, get an advocate">
        <Note>
          <p className="mb-3">
            Free legal aid is a statutory right under the Legal Services
            Authorities Act, 1987 for most people in India — including every
            woman, every child, and anyone below the income limit their State
            sets.
          </p>
          <p>
            NALSA&rsquo;s helpline is{" "}
            <a
              href={`tel:${LEGAL_AID_HELPLINE}`}
              className="font-semibold text-amber-800 underline underline-offset-2"
            >
              {LEGAL_AID_HELPLINE}
            </a>
            . It costs nothing to call and you do not need to qualify in advance
            to ask.
          </p>
        </Note>
      </Section>
    </LegalShell>
  );
}
