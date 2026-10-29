"use client";

import * as React from "react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
} from "recharts";
import type { Event } from "@/types";

interface ImpactChartProps {
  events: Event[];
}

export default function ImpactChart({ events }: ImpactChartProps) {
  // Format data for chart
  const data = events.slice(0, 7).map((e) => {
    const name = e.event_type
      .replace(/_/g, " ")
      .replace(/\b\w/g, (char) => char.toUpperCase());

    return {
      name,
      impact: e.impact_score || Math.round(e.confidence * 100),
      raw: e,
    };
  });

  const getBarColor = (val: number) => {
    if (val >= 80) return "var(--color-negative)"; // critical
    if (val >= 60) return "var(--color-warning)"; // high
    if (val >= 40) return "var(--color-caramel)"; // medium
    return "var(--color-granite-light)"; // low
  };

  return (
    <div className="w-full h-64 font-mono text-xs">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={data}
          margin={{ top: 10, right: 10, left: -25, bottom: 0 }}
        >
          <XAxis 
            dataKey="name" 
            tickLine={false} 
            axisLine={false}
            tick={{ fill: "var(--color-granite)" }}
          />
          <YAxis 
            tickLine={false} 
            axisLine={false}
            tick={{ fill: "var(--color-granite)" }}
            domain={[0, 100]}
          />
          <Tooltip
            cursor={{ fill: "rgba(245, 240, 235, 0.02)" }}
            content={({ active, payload }) => {
              if (active && payload && payload.length) {
                const item = payload[0].payload;
                return (
                  <div className="bg-ash-deep border border-granite/20 p-3 rounded-lg shadow-xl space-y-1">
                    <p className="text-xs font-bold text-silk">{item.name}</p>
                    <p className="text-[10px] text-granite-light">
                      Severity: <span className="text-caramel capitalize font-bold">{item.raw.severity}</span>
                    </p>
                    <p className="text-[10px] text-granite-light">
                      Impact Index: <span className="text-silk font-bold font-data">{item.impact}</span>
                    </p>
                  </div>
                );
              }
              return null;
            }}
          />
          <Bar dataKey="impact" radius={[4, 4, 0, 0]} maxBarSize={30}>
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={getBarColor(entry.impact)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
