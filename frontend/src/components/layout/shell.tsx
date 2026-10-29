"use client";

import * as React from "react";
import { Sidebar } from "./sidebar";
import { Header } from "./header";
import { cn } from "@/lib/utils";

export function Shell({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <div className="flex h-screen w-screen overflow-hidden bg-ash-deep text-silk select-none">
      {/* Side Navigation */}
      <Sidebar className="flex-shrink-0" />

      {/* Main Content Area */}
      <div className="flex flex-col flex-1 min-w-0 overflow-hidden relative">
        {/* Header */}
        <Header />

        {/* Scrollable Viewport */}
        <main className={cn("flex-1 overflow-y-auto p-8 relative scroll-smooth focus:outline-none animate-fade-in", className)}>
          {children}
        </main>
      </div>
    </div>
  );
}
