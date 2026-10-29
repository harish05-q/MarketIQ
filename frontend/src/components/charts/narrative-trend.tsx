"use client";

import * as React from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";
import type { Narrative } from "@/types";

interface NarrativeTrendProps {
  narratives: Narrative[];
}

export default function NarrativeTrend({ narratives }: NarrativeTrendProps) {
  // Aggregate timeline data from narratives
  // Standardize dates and frequency to plot trend
  const plotData = React.useMemo(() => {
    // If narratives have timeline data, merge and plot
    const merged: Record<string, Record<string, number>> = {};
    const narrativeTitles: string[] = [];

    narratives.slice(0, 3).forEach((n) => {
      narrativeTitles.push(n.title);
      if (n.timeline) {
        n.timeline.forEach((pt) => {
          // format date as short version
          const dateLabel = new Date(pt.date).toLocaleDateString("en-US", {
            month: "short",
            day: "numeric",
          });
          if (!merged[dateLabel]) {
            merged[dateLabel] = {};
          }
          merged[dateLabel][n.title] = pt.frequency;
        });
      }
    });

    return {
      titles: narrativeTitles,
      data: Object.entries(merged).map(([date, values]) => ({
        date,
        ...values,
      })).sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime()),
    };
  }, [narratives]);

  const lineColors = [
    "var(--color-caramel)",
    "var(--color-positive)",
    "var(--color-warning)",
  ];

  return (
    <div className="w-full h-64 font-mono text-xs">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={plotData.data}
          margin={{ top: 10, right: 10, left: -25, bottom: 0 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="date" 
            tickLine={false} 
            axisLine={false}
            tick={{ fill: "var(--color-granite)" }}
          />
          <YAxis 
            tickLine={false} 
            axisLine={false}
            tick={{ fill: "var(--color-granite)" }}
          />
          <Tooltip
            content={({ active, payload, label }) => {
              if (active && payload && payload.length) {
                return (
                  <div className="bg-ash-deep border border-granite/20 p-3 rounded-lg shadow-xl space-y-1">
                    <p className="text-xs font-bold text-silk">{label}</p>
                    {payload.map((p, idx) => (
                      <p key={idx} className="text-[10px]" style={{ color: p.color }}>
                        {p.name}: <span className="font-bold font-data">{p.value} articles</span>
                      </p>
                    ))}
                  </div>
                );
              }
              return null;
            }}
          />
          {plotData.titles.map((title, index) => (
            <Line
              key={title}
              type="monotone"
              dataKey={title}
              name={title}
              stroke={lineColors[index % lineColors.length]}
              strokeWidth={2}
              activeDot={{ r: 6 }}
              dot={{ r: 3 }}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
