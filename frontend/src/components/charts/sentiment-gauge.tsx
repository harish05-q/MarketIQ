"use client";

import * as React from "react";
import { ResponsiveContainer, RadialBarChart, RadialBar } from "recharts";
import { cn } from "@/lib/utils";

interface SentimentGaugeProps {
  score: number; // -1.0 to 1.0
  className?: string;
}

export default function SentimentGauge({ score, className }: SentimentGaugeProps) {
  // Convert -1 to 1 score into percentage (0 to 100)
  const percentage = Math.round(((score + 1) / 2) * 100);
  
  const getSentimentLabel = (s: number) => {
    if (s > 0.3) return { text: "Bullish", color: "text-positive" };
    if (s < -0.3) return { text: "Bearish", color: "text-negative" };
    return { text: "Neutral", color: "text-neutral-sent" };
  };

  const sentiment = getSentimentLabel(score);

  const data = [
    {
      name: "Gauge",
      value: percentage,
      fill: score > 0.3 
        ? "var(--color-positive)" 
        : score < -0.3 
          ? "var(--color-negative)" 
          : "var(--color-caramel)",
    },
  ];

  return (
    <div className={cn("relative flex flex-col items-center justify-center w-full h-full", className)}>
      <div className="w-full h-44">
        <ResponsiveContainer width="100%" height="100%">
          <RadialBarChart
            cx="50%"
            cy="50%"
            innerRadius="75%"
            outerRadius="100%"
            barSize={12}
            data={data}
            startAngle={180}
            endAngle={0}
          >
            <RadialBar
              background={{ fill: "rgba(245, 240, 235, 0.04)" }}
              dataKey="value"
              cornerRadius={6}
            />
          </RadialBarChart>
        </ResponsiveContainer>
      </div>

      {/* Centered label */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/3 text-center space-y-1">
        <span className="text-xs font-semibold text-granite-light block uppercase tracking-wider">Market Sentiment</span>
        <h4 className={cn("text-xl font-bold font-data leading-none block", sentiment.color)}>
          {score.toFixed(2)}
        </h4>
        <span className={cn("text-[10px] font-bold uppercase block tracking-wider leading-none", sentiment.color)}>
          {sentiment.text}
        </span>
      </div>
    </div>
  );
}
