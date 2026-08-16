import type { Metadata } from "next";
import Link from "next/link";
import { LegalShell, Section, Bullets } from "@/components/LegalShell";

export const metadata: Metadata = {
  title: "Terms of use — Nyaysetu",
  description:
    "The terms on which Nyaysetu is offered: free, open source, provided as-is, and not a substitute for an advocate.",
};

export default function TermsPage() {
  return (
    <LegalShell
      title="Terms of use"
      lede="Short, because the service is free, open source, and asks very little of you."
      updated="16 August 2026"
    >
      <Section heading="What this is">
        <p>
          Nyaysetu is a free legal-information tool for India. The source is
          published under the MIT licence. There is no subscription, no paid
          tier, and nothing here is for sale.
        </p>
      </Section>

      <Section heading="Provided as-is">
        <p>
          The service is offered without warranty of any kind. It may be
          unavailable, it may be wrong, and it may change without notice. The
          backend runs on a free hosting tier that sleeps when idle, so the
          assistant is sometimes slow to wake or briefly unreachable.
        </p>
        <p>
          Decisions about your legal position are yours, and you are responsible
          for verifying anything here against the official source before acting
          on it. See the{" "}
          <Link href="/disclaimer" className="font-medium text-amber-700 underline underline-offset-2 hover:text-amber-800">
            disclaimer
          </Link>{" "}
          for what that means in practice.
        </p>
      </Section>

      <Section heading="Using it reasonably">
        <Bullets
          items={[
            "Do not use this service to break the law or to harm anyone.",
            "Do not post someone else's personal information to the case board.",
            "Do not present generated documents as though they were drafted or settled by an advocate.",
            "Do not hammer the API hard enough to deny the service to others — it runs on a small free tier shared by everyone using it.",
          ]}
        />
      </Section>

      <Section heading="Accounts">
        <p>
          You are responsible for keeping your password to yourself. Accounts
          that are used to harass others or to post other people&rsquo;s private
          information may be removed. You can delete your own account at any
          time, which also removes your cases, messages and saved deadlines.
        </p>
      </Section>

      <Section heading="Content you post">
        <p>
          What you write stays yours. Posting a case grants only what is needed
          to run the service — storing it and showing it to the lawyers using
          the board. Nothing you post is sold, licensed onward, or used to train
          a model.
        </p>
      </Section>

      <Section heading="The lawyer directory is not a vetting service">
        <p>
          Anyone can register as a lawyer on this platform. Nyaysetu does not
          verify Bar Council enrolment, and listing does not amount to a
          recommendation or a warranty of competence. Check any advocate&rsquo;s
          credentials with the relevant State Bar Council before you rely on
          them.
        </p>
      </Section>

      <Section heading="Changes">
        <p>
          These terms may change as the project does. The page carries the date
          it was last reviewed, and the full history is in the public repository.
        </p>
      </Section>
    </LegalShell>
  );
}
