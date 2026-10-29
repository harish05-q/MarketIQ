"use client";

import * as React from "react";
import { cn } from "@/lib/utils";
import type { SectorSentiment } from "@/types";

interface SectorHeatmapProps {
  sectors: SectorSentiment[];
}

export default function SectorHeatmap({ sectors }: SectorHeatmapProps) {
  const getCellColor = (score: number) => {
    // score ranges from -1.0 to 1.0
    if (score > 0.3) {
      // positive (greens)
      if (score > 0.6) return "bg-positive/20 border-positive text-positive";
      return "bg-positive/10 border-positive/60 text-positive/95";
    } else if (score < -0.3) {
      // negative (reds)
      if (score < -0.6) return "bg-negative/20 border-negative text-negative";
      return "bg-negative/10 border-negative/60 text-negative/95";
    }
    // neutral (caramels/earth)
    return "bg-caramel/10 border-caramel/30 text-caramel-warm";
  };

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 gap-3 w-full">
      {sectors.map((sec) => (
        <div
          key={sec.name}
          className={cn(
            "heatmap-cell p-4 border rounded-lg flex flex-col justify-between h-20 transition-all",
            getCellColor(sec.sentiment_score)
          )}
        >
          {/* Header */}
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold truncate pr-1">{sec.name}</span>
            <span className="text-[10px] font-mono opacity-80">
              {sec.trend === "up" ? "▲" : sec.trend === "down" ? "▼" : "■"}
            </span>
          </div>

          {/* Footer Metrics */}
          <div className="flex items-end justify-between font-mono">
            <div>
              <span className="text-[8px] uppercase block opacity-60">Score</span>
              <span className="text-xs font-bold font-data">
                {sec.sentiment_score.toFixed(2)}
              </span>
            </div>
            <div className="text-right">
              <span className="text-[8px] uppercase block opacity-60">Articles</span>
              <span className="text-xs font-bold font-data">{sec.article_count}</span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
