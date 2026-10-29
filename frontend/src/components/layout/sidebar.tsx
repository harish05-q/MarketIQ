"use client";

import * as React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  Activity, Newspaper, Layers, Building2, MessageSquareCode, 
  BookOpenCheck, Settings, ShieldAlert, BarChart3, HelpCircle
} from "lucide-react";
import { cn } from "@/lib/utils";

interface SidebarItem {
  name: string;
  href: string;
  icon: React.ComponentType<any>;
}

const SIDEBAR_ITEMS: SidebarItem[] = [
  { name: "Market Pulse", href: "/", icon: Activity },
  { name: "News Explorer", href: "/news", icon: Newspaper },
  { name: "Narratives", href: "/narratives", icon: Layers },
  { name: "Ask MarketIQ", href: "/ask", icon: MessageSquareCode },
  { name: "Daily Brief", href: "/briefings", icon: BookOpenCheck },
];

export function Sidebar({ className }: { className?: string }) {
  const pathname = usePathname();

  return (
    <aside className={cn("w-60 glass-sidebar flex flex-col h-full", className)}>
      {/* Brand Logo Header */}
      <div className="h-16 flex items-center px-6 border-b border-granite/10">
        <Link href="/" className="flex items-center space-x-2.5 group">
          <div className="w-8 h-8 rounded bg-caramel flex items-center justify-center text-ash-deep font-bold font-mono text-base tracking-tight transition-transform group-hover:scale-105 shadow-md shadow-caramel/10">
            M
          </div>
          <div>
            <span className="font-bold text-silk text-sm tracking-tight block">MarketIQ</span>
            <span className="text-[9px] font-mono text-caramel tracking-wider uppercase block font-bold leading-none">INTELLIGENCE</span>
          </div>
        </Link>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 px-4 py-6 space-y-1.5 overflow-y-auto">
        {SIDEBAR_ITEMS.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;
          
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center space-x-3 px-3 py-2.5 rounded-lg text-xs font-semibold transition-all group relative",
                isActive
                  ? "bg-caramel text-ash-deep shadow shadow-caramel/10"
                  : "text-granite-light hover:text-silk hover:bg-ash-light/20"
              )}
            >
              <Icon className={cn("w-4 h-4 transition-transform", !isActive && "group-hover:scale-110")} />
              <span>{item.name}</span>
              {isActive && (
                <span className="absolute right-2 w-1.5 h-1.5 rounded-full bg-ash-deep" />
              )}
            </Link>
          );
        })}
      </nav>

      {/* Bottom Footer Details */}
      <div className="p-4 border-t border-granite/10 space-y-4">
        {/* Market Status Ticker */}
        <div className="bg-ash-deep/60 rounded-lg p-3 border border-granite/5 flex flex-col space-y-1.5">
          <div className="flex items-center justify-between text-[9px] font-mono">
            <span className="text-granite-light">SYSTEM DATA STATUS</span>
            <span className="text-positive flex items-center font-bold">
              <span className="w-1 h-1 rounded-full bg-positive inline-block mr-1 animate-pulse" />
              LIVE
            </span>
          </div>
          <div className="flex items-center justify-between text-[10px] font-mono">
            <span className="text-silk font-bold">SPX INDEX</span>
            <span className="text-positive font-bold">+0.42%</span>
          </div>
        </div>

        {/* Settings/User profile placeholder */}
        <div className="flex items-center justify-between text-xs text-granite-light px-2">
          <div className="flex items-center space-x-2">
            <div className="w-6 h-6 rounded-full bg-granite/30 border border-granite/20 flex items-center justify-center text-[10px] text-silk font-mono font-bold">
              AI
            </div>
            <span className="font-semibold text-silk-muted text-[11px]">Staff Architect</span>
          </div>
          <button className="hover:text-caramel transition-colors p-1">
            <Settings className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </aside>
  );
}
