"use client";

import * as React from "react";
import { useRouter, usePathname } from "next/navigation";
import { MessageSquareCode, Bell, Search, RefreshCw } from "lucide-react";
import { Button, Input } from "@/components/ui";

export function Header() {
  const pathname = usePathname();
  const router = useRouter();
  const [currentTime, setCurrentTime] = React.useState<string>("");
  const [isRefreshing, setIsRefreshing] = React.useState<boolean>(false);

  React.useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setCurrentTime(
        now.toLocaleTimeString("en-US", {
          hour12: false,
          hour: "2-digit",
          minute: "2-digit",
          second: "2-digit",
        })
      );
    };

    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  const getPageTitle = (path: string) => {
    if (path === "/") return "Market Pulse Overview";
    if (path.startsWith("/news")) return "Financial News Explorer";
    if (path.startsWith("/narratives")) return "Thematic Narrative Trends";
    if (path.startsWith("/ask")) return "Ask MarketIQ Chat";
    if (path.startsWith("/briefings")) return "AI Market Briefing Center";
    if (path.startsWith("/companies")) return "Company Intelligence Profile";
    return "MarketIQ Platform";
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    // Simulate refresh trigger
    try {
      await fetch("http://localhost:8000/api/v1/ingest", { method: "POST" });
    } catch {}
    setTimeout(() => {
      setIsRefreshing(false);
      window.location.reload();
    }, 1500);
  };

  return (
    <header className="h-16 glass-header flex items-center justify-between px-8 sticky top-0 z-40">
      {/* Title */}
      <div className="flex items-center space-x-4">
        <h2 className="text-sm font-bold text-silk uppercase tracking-wider">
          {getPageTitle(pathname)}
        </h2>
      </div>

      {/* Actions */}
      <div className="flex items-center space-x-6">
        {/* Terminal Clock */}
        <div className="hidden sm:flex items-center space-x-2 font-mono text-xs bg-ash-deep border border-granite/10 px-3 py-1 rounded">
          <span className="text-granite-light">EST TIME</span>
          <span className="text-caramel font-semibold font-data">{currentTime}</span>
        </div>

        {/* Global Search trigger or ask button */}
        {pathname !== "/ask" && (
          <Button
            variant="outline"
            size="sm"
            className="hidden md:flex items-center text-xs space-x-1.5 h-8 border-caramel/20 hover:border-caramel text-caramel hover:bg-caramel/5"
            onClick={() => router.push("/ask")}
          >
            <MessageSquareCode className="w-3.5 h-3.5" />
            <span>Ask MarketIQ</span>
          </Button>
        )}

        {/* Refresh pipeline button */}
        <Button
          variant="ghost"
          size="icon"
          onClick={handleRefresh}
          className="text-granite-light hover:text-silk h-8 w-8 relative"
          title="Force Fetch RSS Feeds"
        >
          <RefreshCw className={`w-4 h-4 ${isRefreshing ? "animate-spin text-caramel" : ""}`} />
        </Button>

        {/* Notification Bell */}
        <div className="relative">
          <Button
            variant="ghost"
            size="icon"
            className="text-granite-light hover:text-silk h-8 w-8"
          >
            <Bell className="w-4 h-4" />
          </Button>
          <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 rounded-full bg-caramel ring-2 ring-ash-deep animate-pulse" />
        </div>
      </div>
    </header>
  );
}
