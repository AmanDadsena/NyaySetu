"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { 
  FileText, 
  Wrench, 
  Scale, 
  FolderOpen, 
  BookOpen, 
  MessageSquare, 
  Info,
  PanelLeftClose,
  PanelLeftOpen,
  LogOut
} from "lucide-react";
import { useT } from "@/lib/i18n/LanguageProvider";
import type { TranslationKey } from "@/lib/i18n/translations";
import { useAuth } from "@/lib/auth/AuthProvider";
import { cn } from "@/lib/utils";
import { LanguageSwitcher } from "@/components/LanguageSwitcher";

const NAV_ITEMS: { href: string; key: TranslationKey; icon: any; badge?: number }[] = [
  { href: "/analyze", key: "nav.analyze", icon: FileText },
  { href: "/toolkit", key: "nav.toolkit", icon: Wrench },
  { href: "/lawyers", key: "nav.lawyers", icon: Scale },
  { href: "/cases", key: "nav.cases", icon: FolderOpen },
  { href: "/knowledge", key: "nav.knowledge", icon: BookOpen },
  { href: "/messages", key: "nav.messages", icon: MessageSquare, badge: 3 },
  { href: "/about", key: "nav.about", icon: Info },
];

export function Sidebar() {
  const pathname = usePathname();
  const t = useT();
  const { user, ready, signOut } = useAuth();
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [hoveredPath, setHoveredPath] = useState<string | null>(null);

  const sidebarVariants = {
    expanded: { width: 280 },
    collapsed: { width: 80 }
  };

  const textVariants = {
    hidden: { opacity: 0, x: -10, display: "none" },
    visible: { 
      opacity: 1, 
      x: 0, 
      display: "block",
      transition: { delay: 0.1, duration: 0.2 }
    }
  };

  return (
    <motion.nav 
      initial={false}
      animate={isCollapsed ? "collapsed" : "expanded"}
      variants={sidebarVariants}
      transition={{ type: "spring", stiffness: 300, damping: 30 }}
      className="relative h-full bg-slate-50/70 backdrop-blur-2xl border-r border-slate-200/50 flex flex-col pt-6 pb-6 sticky top-0 z-40 shrink-0 shadow-[4px_0_24px_-12px_rgba(0,0,0,0.05)] overflow-visible"
    >
      {/* Background Gradient Wash */}
      <div className="absolute inset-0 bg-gradient-to-b from-amber-50/30 to-slate-50/10 pointer-events-none -z-10" />

      {/* Collapse Toggle */}
      <button 
        onClick={() => setIsCollapsed(!isCollapsed)}
        className="absolute -right-3.5 top-8 z-50 p-1.5 bg-white border border-slate-200/60 rounded-full shadow-sm hover:shadow-md text-slate-400 hover:text-slate-900 transition-all active:scale-95"
      >
        {isCollapsed ? <PanelLeftOpen className="w-4 h-4" /> : <PanelLeftClose className="w-4 h-4" />}
      </button>

      {/* Logo Section */}
      <Link href="/" className="flex items-center gap-3 px-6 mb-10 group shrink-0 overflow-hidden">
        <div className="relative flex items-center justify-center w-8 h-8 min-w-8 rounded-xl overflow-hidden shadow-[0_2px_10px_-2px_rgba(0,0,0,0.1)] group-hover:shadow-[0_4px_16px_-4px_rgba(0,0,0,0.15)] group-hover:scale-105 transition-all duration-400 border border-slate-200/80 bg-white">
          <img src="/logo.png" alt="Nyaysetu Logo" className="w-full h-full object-cover relative z-10" />
          {/* Subtle logo pulse glow */}
          <div className="absolute inset-0 bg-amber-400/20 blur-md animate-pulse opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
        </div>
        
        <AnimatePresence mode="popLayout">
          {!isCollapsed && (
            <motion.span 
              variants={textVariants}
              initial="hidden"
              animate="visible"
              exit="hidden"
              className="text-2xl tracking-tight flex items-center font-serif whitespace-nowrap"
            >
              <span className="font-bold text-slate-900">Nyay</span>
              <span className="font-semibold text-amber-600 drop-shadow-[0_0_12px_rgba(217,119,6,0.2)]">setu</span>
            </motion.span>
          )}
        </AnimatePresence>
      </Link>

      {/* Main Nav Links */}
      <div className="flex-1 flex flex-col gap-1.5 px-3 relative" onMouseLeave={() => setHoveredPath(null)}>
        {NAV_ITEMS.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`);
          const isHovered = hoveredPath === item.href;
          const Icon = item.icon;
          
          return (
            <Link
              key={item.href}
              href={item.href}
              onMouseEnter={() => setHoveredPath(item.href)}
              className={cn(
                "group relative flex items-center px-3 py-2.5 rounded-xl text-sm font-medium transition-colors outline-none",
                isActive ? "text-slate-900" : "text-slate-500"
              )}
            >
              {/* Active Indicator Background */}
              {isActive && (
                <motion.div
                  layoutId="sidebar-active-pill"
                  className="absolute inset-0 bg-white border border-slate-200/60 shadow-[0_1px_3px_0_rgba(0,0,0,0.05),0_1px_2px_-1px_rgba(0,0,0,0.05)] rounded-xl"
                  transition={{ type: "spring", stiffness: 400, damping: 30 }}
                />
              )}

              {/* Hover Indicator Background */}
              {!isActive && isHovered && (
                <motion.div
                  layoutId="sidebar-hover-pill"
                  className="absolute inset-0 bg-slate-200/30 rounded-xl"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ type: "spring", stiffness: 400, damping: 30 }}
                />
              )}

              <div className="relative z-10 flex items-center gap-3 w-full justify-center lg:justify-start">
                <div className="relative flex items-center justify-center">
                  <Icon 
                    className={cn(
                      "h-5 w-5 transition-all duration-300", 
                      isActive 
                        ? "text-amber-600 scale-110 drop-shadow-[0_2px_4px_rgba(217,119,6,0.3)]" 
                        : "text-slate-400 group-hover:text-slate-700 group-hover:scale-110"
                    )} 
                  />
                  {/* Notification Badge */}
                  {item.badge && (
                    <motion.div 
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ type: "spring", delay: 0.2 }}
                      className={cn(
                        "absolute -top-1.5 -right-1.5 bg-red-500 text-white text-[10px] font-bold h-4 w-4 rounded-full flex items-center justify-center border-2 border-white shadow-sm transition-transform duration-300",
                        isCollapsed ? "-right-1 -top-1 h-3 w-3 text-transparent" : "",
                        isActive ? "border-white" : "border-slate-50 group-hover:border-slate-100"
                      )}
                    >
                      {!isCollapsed && item.badge}
                    </motion.div>
                  )}
                </div>

                <AnimatePresence mode="popLayout">
                  {!isCollapsed && (
                    <motion.span 
                      variants={textVariants}
                      initial="hidden"
                      animate="visible"
                      exit="hidden"
                      className="whitespace-nowrap"
                    >
                      {t(item.key)}
                    </motion.span>
                  )}
                </AnimatePresence>
              </div>

              {/* Tooltip for collapsed mode */}
              <AnimatePresence>
                {isCollapsed && isHovered && (
                  <motion.div
                    initial={{ opacity: 0, x: -5, scale: 0.95 }}
                    animate={{ opacity: 1, x: 0, scale: 1 }}
                    exit={{ opacity: 0, x: -5, scale: 0.95 }}
                    transition={{ duration: 0.15 }}
                    className="absolute left-full ml-4 px-2.5 py-1.5 bg-slate-800 text-slate-50 text-xs font-semibold rounded-lg shadow-xl whitespace-nowrap z-50 flex items-center"
                  >
                    <div className="absolute -left-1 top-1/2 -translate-y-1/2 w-2 h-2 bg-slate-800 rotate-45" />
                    {t(item.key)}
                    {item.badge && (
                      <span className="ml-2 bg-red-500 text-white px-1.5 py-0.5 rounded-full text-[9px]">
                        {item.badge}
                      </span>
                    )}
                  </motion.div>
                )}
              </AnimatePresence>
            </Link>
          );
        })}
      </div>

      {/* Beautiful Separator */}
      <div className="w-full h-px bg-gradient-to-r from-transparent via-slate-200 to-transparent opacity-80 my-2" />

      {/* Bottom Area */}
      <div className="mt-auto px-3 flex flex-col gap-3">
        <div className={cn("transition-all duration-300 flex justify-center", isCollapsed ? "px-0" : "px-2")}>
          {!isCollapsed ? (
             <LanguageSwitcher />
          ) : (
            <div className="h-8 w-8 rounded-full bg-slate-200/50 flex items-center justify-center text-xs font-medium text-slate-500 cursor-pointer hover:bg-slate-200 transition-colors">
              Aa
            </div>
          )}
        </div>
        
        {!ready ? (
          <div className="h-12 w-full rounded-xl bg-slate-200/50 animate-pulse" />
        ) : user ? (
          <div className={cn(
            "group relative flex items-center gap-3 p-1.5 bg-white border border-slate-200/60 rounded-2xl shadow-sm hover:shadow-md transition-all duration-300",
            isCollapsed ? "justify-center" : ""
          )}>
            {/* Avatar with Gradient Ring */}
            <div className="relative shrink-0 flex items-center justify-center">
              <div className="absolute inset-0 rounded-full bg-gradient-to-tr from-amber-400 to-amber-600 opacity-20 blur-sm group-hover:opacity-40 transition-opacity duration-300" />
              <div className="relative flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-amber-100 to-amber-50 border border-amber-200/50 text-sm font-bold text-amber-800 shadow-inner z-10 group-hover:scale-105 transition-transform duration-300">
                {user.name.charAt(0).toUpperCase()}
              </div>
            </div>

            <AnimatePresence mode="popLayout">
              {!isCollapsed && (
                <motion.div 
                  variants={textVariants}
                  initial="hidden"
                  animate="visible"
                  exit="hidden"
                  className="flex flex-col min-w-0 flex-1 pr-2"
                >
                  <span className="truncate text-sm font-semibold text-slate-900 group-hover:text-amber-700 transition-colors">{user.name}</span>
                  <button 
                    onClick={signOut}
                    className="flex items-center gap-1 text-left text-xs font-medium text-slate-400 hover:text-red-500 transition-colors"
                  >
                    <LogOut className="w-3 h-3" />
                    <span>{t("nav.signOut")}</span>
                  </button>
                </motion.div>
              )}
            </AnimatePresence>

            {isCollapsed && (
              <div className="absolute left-full ml-4 opacity-0 pointer-events-none group-hover:opacity-100 group-hover:pointer-events-auto px-3 py-2 bg-white border border-slate-200/60 text-slate-700 text-xs font-medium rounded-xl shadow-xl whitespace-nowrap z-50 transition-all duration-200 translate-x-[-4px] group-hover:translate-x-0">
                <div className="absolute -left-1 top-1/2 -translate-y-1/2 w-2 h-2 bg-white border-l border-b border-slate-200/60 rotate-45" />
                <div className="font-semibold text-slate-900 mb-0.5">{user.name}</div>
                <button onClick={signOut} className="text-red-500 hover:text-red-600 flex items-center gap-1">
                  <LogOut className="w-3 h-3" /> Sign out
                </button>
              </div>
            )}
          </div>
        ) : (
          <div className="flex flex-col gap-2">
            {!isCollapsed ? (
              <>
                <Link
                  href="/login"
                  className="px-3 py-2 text-sm font-medium text-slate-600 hover:text-slate-900 transition-colors text-center"
                >
                  {t("nav.login")}
                </Link>
                <Link
                  href="/register"
                  className="bg-slate-900 text-white px-3 py-2.5 rounded-xl text-sm font-medium text-center hover:bg-slate-800 shadow-sm transition-all active:scale-[0.98]"
                >
                  {t("nav.register")}
                </Link>
              </>
            ) : (
              <Link
                href="/login"
                className="h-9 w-9 rounded-full bg-slate-900 text-white flex items-center justify-center hover:bg-slate-800 shadow-sm transition-all active:scale-95 mx-auto"
                title={t("nav.login")}
              >
                <LogOut className="w-4 h-4" />
              </Link>
            )}
          </div>
        )}
      </div>
    </motion.nav>
  );
}
