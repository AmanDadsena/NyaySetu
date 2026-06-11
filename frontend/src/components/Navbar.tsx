"use client";

import Link from "next/link";
import { Scale, Hexagon } from "lucide-react";
import { usePathname } from "next/navigation";

export function Navbar() {
  const pathname = usePathname();

  return (
    <nav className="w-full bg-white/80 backdrop-blur-xl border-b border-gray-100 sticky top-0 z-50">
      <div className="px-6 py-4 flex items-center justify-between max-w-7xl mx-auto">
        {/* Left: Logo */}
        <Link href="/" className="flex items-center gap-3 group">
          <div className="relative flex items-center justify-center w-10 h-10 rounded-xl overflow-hidden shadow-sm group-hover:shadow-md group-hover:scale-105 transition-all duration-300 border border-gray-100">
            <img src="/logo.png" alt="Nyaysetu Logo" className="w-full h-full object-cover" />
          </div>
          <span className="text-xl tracking-tight flex items-center font-serif">
            <span className="font-bold text-slate-900">Nyay</span>
            <span className="font-medium text-amber-600">setu</span>
          </span>
        </Link>

        {/* Center: Links */}
        <div className="hidden md:flex items-center gap-8">
          <Link
            href="/analyze"
            className={`text-sm font-medium transition-colors ${
              pathname === "/analyze" ? "text-black" : "text-gray-600 hover:text-black"
            }`}
          >
            Analyze
          </Link>
          <Link
            href="/lawyers"
            className={`text-sm font-medium transition-colors ${
              pathname === "/lawyers" ? "text-black" : "text-gray-600 hover:text-black"
            }`}
          >
            Find Lawyer
          </Link>
          <Link
            href="/cases"
            className={`text-sm font-medium transition-colors ${
              pathname === "/cases" ? "text-slate-900" : "text-gray-600 hover:text-slate-900"
            }`}
          >
            Case Board
          </Link>
          <Link
            href="/knowledge"
            className={`text-sm font-medium transition-colors ${
              pathname === "/knowledge" ? "text-amber-600" : "text-gray-600 hover:text-amber-600"
            }`}
          >
            Knowledge Base
          </Link>
          <Link
            href="/messages"
            className={`text-sm font-medium transition-colors ${
              pathname === "/messages" ? "text-slate-900" : "text-gray-600 hover:text-slate-900"
            }`}
          >
            Discussions
          </Link>
          <Link
            href="/about"
            className={`text-sm font-medium transition-colors ${
              pathname === "/about" ? "text-black" : "text-gray-600 hover:text-black"
            }`}
          >
            About Us
          </Link>
        </div>

        {/* Right: Auth */}
        <div className="flex items-center gap-6">
          <Link
            href="/login"
            className="text-sm text-gray-600 hover:text-black font-medium"
          >
            Login
          </Link>
          <Link
            href="/register"
            className="bg-black text-white px-5 py-2.5 rounded-full text-sm font-medium hover:bg-gray-800 shadow-sm transition-colors"
          >
            Get started free
          </Link>
        </div>
      </div>
    </nav>
  );
}
