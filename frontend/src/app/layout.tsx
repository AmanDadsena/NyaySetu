import type { Metadata } from "next";
import { Inter, JetBrains_Mono, Source_Serif_4 } from "next/font/google";
import { cookies } from "next/headers";
import "./globals.css";
import { Navbar } from "@/components/Navbar";
import { Chatbot } from "@/components/Chatbot";
import { LanguageProvider } from "@/lib/i18n/LanguageProvider";
import { LOCALE_COOKIE, normalizeLocale } from "@/lib/i18n/locales";
import { AuthProvider } from "@/lib/auth/AuthProvider";

const fontSans = Inter({
  subsets: ["latin"],
  variable: "--font-geist-sans",
  display: "swap",
  fallback: ["system-ui", "arial"],
  preload: false,
});

const fontMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-geist-mono",
  display: "swap",
  fallback: ["ui-monospace", "monospace"],
  preload: false,
});

// Display face for headings and the wordmark. A serif with weight range rather
// than a single-weight display face, so the bold wordmark is a real bold and
// not a synthesised one. Latin only — Indic headings fall through to the
// script-specific stack declared in globals.css.
const fontSerif = Source_Serif_4({
  subsets: ["latin"],
  weight: ["400", "600", "700"],
  style: ["normal", "italic"],
  variable: "--font-display",
  display: "swap",
  fallback: ["Georgia", "serif"],
  preload: false,
});

export const metadata: Metadata = {
  title: "Nyaysetu — AI-Powered Legal Document Analysis",
  description:
    "Paste raw legal text and get AI-powered clause extraction, risk analysis, and plain-language summaries in seconds.",
};

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  // Resolving the locale on the server means the first paint is already in the
  // user's language — no flash of English for the users who need it least.
  const locale = normalizeLocale((await cookies()).get(LOCALE_COOKIE)?.value);

  return (
    <html
      lang={locale}
      className={`${fontSans.variable} ${fontMono.variable} ${fontSerif.variable} h-full antialiased`}
      suppressHydrationWarning
    >
      <body className="min-h-full flex flex-col bg-white text-black">
        <LanguageProvider initialLocale={locale}>
          <AuthProvider>
            <Navbar />
            {children}
            <Chatbot />
          </AuthProvider>
        </LanguageProvider>
      </body>
    </html>
  );
}
