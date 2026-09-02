"use client";

import { usePathname } from "next/navigation";
import { Navbar } from "./Navbar";
import { Sidebar } from "./Sidebar";
import { Footer } from "./Footer";
import { PageTransition } from "./motion/PageTransition";

export function AppLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  
  // Define routes that should use the Landing Page layout (Top Navbar + Footer)
  const isLandingPage = pathname === "/" || pathname === "/about" || pathname === "/how-it-works" || pathname === "/privacy" || pathname === "/terms" || pathname === "/disclaimer" || pathname === "/contact";

  if (isLandingPage) {
    return (
      <div className="flex flex-col min-h-screen">
        <Navbar />
        <div className="flex-1">
          <PageTransition>{children}</PageTransition>
        </div>
        <Footer />
      </div>
    );
  }

  // App Layout (Sidebar on desktop, mobile nav on mobile)
  return (
    <div className="flex h-screen overflow-hidden bg-slate-50">
      <div className="hidden md:block">
        <Sidebar />
      </div>
      <div className="md:hidden">
        {/* We reuse the Navbar for mobile since it has a hamburger menu */}
        <Navbar />
      </div>
      <main className="flex-1 overflow-y-auto">
        <PageTransition>{children}</PageTransition>
      </main>
    </div>
  );
}
