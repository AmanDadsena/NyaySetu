"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";
import { 
  FileText, 
  Wrench, 
  Scale, 
  FolderOpen, 
  BookOpen, 
  MessageSquare, 
  Info,
  Menu,
  X,
  LogOut,
  User as UserIcon
} from "lucide-react";
import { useT } from "@/lib/i18n/LanguageProvider";
import type { TranslationKey } from "@/lib/i18n/translations";
import { useAuth } from "@/lib/auth/AuthProvider";
import { cn } from "@/lib/utils";
import { LanguageSwitcher } from "@/components/LanguageSwitcher";

const NAV_ITEMS: { href: string; key: TranslationKey; icon: any }[] = [
  { href: "/analyze", key: "nav.analyze", icon: FileText },
  { href: "/toolkit", key: "nav.toolkit", icon: Wrench },
  { href: "/lawyers", key: "nav.lawyers", icon: Scale },
  { href: "/cases", key: "nav.cases", icon: FolderOpen },
  { href: "/knowledge", key: "nav.knowledge", icon: BookOpen },
  { href: "/messages", key: "nav.messages", icon: MessageSquare },
  { href: "/about", key: "nav.about", icon: Info },
];

export function Sidebar() {
  const pathname = usePathname();
  const t = useT();
  const { user, ready, signOut } = useAuth();
  
  return (
    <nav className="w-64 h-full bg-slate-50/50 backdrop-blur-xl border-r border-slate-200/50 flex flex-col pt-6 pb-4 px-4 sticky top-0 z-40 shrink-0">
      {/* Logo */}
      <Link href="/" className="flex items-center gap-3 px-2 mb-10 group">
        <div className="relative flex items-center justify-center w-8 h-8 rounded-xl overflow-hidden shadow-sm group-hover:shadow-md group-hover:scale-105 transition-all duration-300 border border-slate-200/60 bg-white">
          <img src="/logo.png" alt="Nyaysetu Logo" className="w-full h-full object-cover" />
        </div>
        <span className="text-xl tracking-tight flex items-center font-serif">
          <span className="font-bold text-slate-900">Nyay</span>
          <span className="font-medium text-amber-600">setu</span>
        </span>
      </Link>

      {/* Main Nav Links */}
      <div className="flex-1 flex flex-col gap-1.5 relative">
        {NAV_ITEMS.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`);
          const Icon = item.icon;
          
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "group relative flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors",
                isActive ? "text-slate-900" : "text-slate-500 hover:text-slate-900"
              )}
            >
              {isActive && (
                <motion.div
                  layoutId="sidebar-active-pill"
                  className="absolute inset-0 bg-white border border-slate-200/60 shadow-sm rounded-xl"
                  transition={{ type: "spring", stiffness: 400, damping: 30 }}
                />
              )}
              <div className="relative z-10 flex items-center gap-3 w-full">
                <Icon className={cn("h-4 w-4 transition-colors", isActive ? "text-amber-600" : "text-slate-400 group-hover:text-amber-500")} />
                {t(item.key)}
              </div>
            </Link>
          );
        })}
      </div>

      {/* Bottom Area: Language + User */}
      <div className="mt-auto pt-6 flex flex-col gap-4 border-t border-slate-200/50">
        <div className="px-2">
          <LanguageSwitcher />
        </div>
        
        {!ready ? (
          <div className="h-12 w-full rounded-xl bg-slate-200/50 animate-pulse" />
        ) : user ? (
          <div className="flex items-center gap-3 px-3 py-2.5 bg-white border border-slate-200/60 rounded-xl shadow-sm">
            <span className="flex shrink-0 h-8 w-8 items-center justify-center rounded-full bg-amber-100 text-xs font-bold text-amber-800">
              {user.name.charAt(0).toUpperCase()}
            </span>
            <div className="flex flex-col min-w-0 flex-1">
              <span className="truncate text-sm font-semibold text-slate-900">{user.name}</span>
              <button 
                onClick={signOut}
                className="text-left text-xs font-medium text-slate-500 hover:text-red-600 transition-colors"
              >
                {t("nav.signOut")}
              </button>
            </div>
          </div>
        ) : (
          <div className="flex flex-col gap-2">
            <Link
              href="/login"
              className="px-3 py-2 text-sm font-medium text-slate-600 hover:text-slate-900 transition-colors"
            >
              {t("nav.login")}
            </Link>
            <Link
              href="/register"
              className="bg-slate-900 text-white px-3 py-2.5 rounded-xl text-sm font-medium text-center hover:bg-slate-800 shadow-sm transition-all active:scale-[0.98]"
            >
              {t("nav.register")}
            </Link>
          </div>
        )}
      </div>
    </nav>
  );
}
