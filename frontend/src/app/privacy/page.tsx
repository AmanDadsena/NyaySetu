import type { Metadata } from "next";
import { LegalShell, Section, Note, Bullets } from "@/components/LegalShell";

export const metadata: Metadata = {
  title: "Privacy — Nyaysetu",
  description:
    "What Nyaysetu stores, what it does not, and how to remove your account. Written from the actual database schema.",
};

export default function PrivacyPage() {
  return (
    <LegalShell
      title="Privacy"
      lede="These are people's legal problems. This page describes exactly what the application stores, written from the database schema rather than from a template."
      updated="16 August 2026"
    >
      <Section heading="You can use most of this without an account">
        <p>
          The assistant, the whole toolkit — deadlines, forum routing, court
          fees, document drafting, stamp duty, maintenance, citations — and the
          knowledge base all work without signing in. If you never register,
          this application stores nothing that identifies you.
        </p>
        <p>
          An account is needed only for the parts that are inherently
          person-to-person: posting a case to the board, and messaging about it.
        </p>
      </Section>

      <Section heading="What is stored if you do register">
        <p>Your account row holds:</p>
        <Bullets
          items={[
            "Your name and email address.",
            "A hash of your password — never the password itself.",
            'Your role, either "client" or "lawyer".',
            "The dates the account was created and last changed.",
            "If you registered as a lawyer: your stated specialties, years of experience, and Bar Council number if you supplied one.",
          ]}
        />
        <p>
          Cases you post store their title, description, status, and the account
          that posted them. Messages store their text, who sent them, who
          received them, and which case they belong to. Deadlines you save store
          the rule and the dates you entered.
        </p>
      </Section>

      <Section heading="Messages are not end-to-end encrypted">
        <Note tone="warn">
          <p className="mb-3 font-semibold">
            Please read this before typing anything sensitive into the messaging
            feature.
          </p>
          <p>
            Message text is stored in the database as plain text. Transport
            between your browser and the server is encrypted by HTTPS, but
            whoever operates the server can read what you send. This is not
            end-to-end encryption and should not be relied on as if it were.
          </p>
        </Note>
        <p>
          An earlier version of this site displayed an &ldquo;End-to-end
          Encrypted&rdquo; badge on the messaging screen. That badge was
          inaccurate and has been removed. For anything you would not want the
          operator of this service to read, speak to an advocate directly —
          communications with your advocate carry a legal privilege that
          messages here do not.
        </p>
      </Section>

      <Section heading="The retrieval feedback log">
        <p>
          To find out where the corpus is thin, the backend can record when
          retrieval fails to find a good match. This is <strong>off unless
          explicitly enabled</strong> by the operator through an environment
          variable, and even when on it deliberately stores very little:
        </p>
        <Bullets
          items={[
            "No user id, no account, no IP address.",
            "A session key that groups two consecutive requests and maps to nothing else.",
            "The text of your question only if a second, separate flag is also set.",
            "The log file is excluded from version control.",
          ]}
        />
      </Section>

      <Section heading="In your browser">
        <Bullets
          items={[
            "A locale cookie, so the page loads in your language rather than flashing English first.",
            "If you sign in, a session token in local storage. Clearing your browser data signs you out.",
            "Toolkit lookup tables cached locally, so the deadline calculator keeps working without a network connection.",
          ]}
        />
        <p>
          There is no advertising, no analytics product, and no third-party
          tracking script on this site.
        </p>
      </Section>

      <Section heading="Voice">
        <p>
          Dictation and read-aloud use the Web Speech API built into your
          browser. Depending on your browser and platform, audio may be sent to
          that vendor for recognition. Nyaysetu neither receives nor stores
          audio. If this matters to you, type instead of dictating.
        </p>
      </Section>

      <Section heading="Deleting your account">
        <p>
          You can delete your own account from the application. Deleting it
          removes your cases, the messages you sent and received, and the
          deadlines you saved, through database-level cascade rules rather than
          a background job that might silently fail.
        </p>
      </Section>

      <Section heading="Where this runs">
        <p>
          The frontend is served by Vercel and the backend runs as a Hugging
          Face Space, with data in a Postgres database. Those providers process
          data on the operator&rsquo;s behalf in order to run the service.
        </p>
      </Section>
    </LegalShell>
  );
}
