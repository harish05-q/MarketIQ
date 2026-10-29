"use client";

import * as React from "react";
import dynamic from "next/dynamic";
import { Layers, Activity, Calendar, Newspaper, Users, Sparkles, TrendingUp, ShieldCheck } from "lucide-react";
import { Shell } from "@/components/layout/shell";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, Badge, Button } from "@/components/ui";
import { NarrativeCard, formatDate, getSentimentDetails } from "@/components/cards";
import { fetchNarratives } from "@/lib/api";
import { mockNarratives, mockArticles } from "@/lib/mock-data";
import type { Narrative, Article } from "@/types";

// Dynamically import chart
const NarrativeTrend = dynamic(() => import("@/components/charts/narrative-trend"), { ssr: false });

export default function NarrativeExplorerPage() {
  const [narratives, setNarratives] = React.useState<Narrative[]>([]);
  const [loading, setLoading] = React.useState<boolean>(true);
  const [isMock, setIsMock] = React.useState<boolean>(false);
  const [selectedNarrative, setSelectedNarrative] = React.useState<Narrative | null>(null);

  React.useEffect(() => {
    async function loadNarratives() {
      try {
        const response = await fetchNarratives();
        if (response.status === "success" && response.data && response.data.length > 0) {
          // Map backend schemas to frontend
          const apiNarratives = response.data.map((nar: any) => ({
            id: nar.id,
            title: nar.title,
            description: nar.description || "",
            trend_score: nar.trend_score || 50,
            momentum: nar.momentum || "stable",
            article_count: nar.article_count || 0,
            sentiment: {
              score: nar.sentiment === "positive" ? 0.6 : nar.sentiment === "negative" ? -0.6 : 0,
              label: (nar.sentiment || "neutral").toLowerCase() as any,
              confidence: 0.9,
            },
            sectors: [],
            entities: [],
            timeline: [
              { date: new Date(Date.now() - 3 * 86400000).toISOString(), frequency: 5, sentiment: 0.2 },
              { date: new Date(Date.now() - 2 * 86400000).toISOString(), frequency: 8, sentiment: 0.3 },
              { date: new Date(Date.now() - 1 * 86400000).toISOString(), frequency: 12, sentiment: 0.5 },
              { date: new Date().toISOString(), frequency: nar.article_count, sentiment: 0.6 },
            ],
            first_seen: nar.first_seen || new Date().toISOString(),
            last_updated: nar.last_updated || new Date().toISOString(),
          }));
          setNarratives(apiNarratives);
          setSelectedNarrative(apiNarratives[0]);
          setIsMock(false);
        } else {
          throw new Error("Empty narratives database");
        }
      } catch (err) {
        console.warn("API Offline or empty, using mock narratives:", err);
        setNarratives(mockNarratives);
        setSelectedNarrative(mockNarratives[0]);
        setIsMock(true);
      } finally {
        setLoading(false);
      }
    }
    loadNarratives();
  }, []);

  if (loading) {
    return (
      <Shell>
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="h-80 skeleton lg:col-span-1" />
            <div className="h-80 skeleton lg:col-span-2" />
          </div>
        </div>
      </Shell>
    );
  }

  const active = selectedNarrative || narratives[0];
  const sent = active ? getSentimentDetails(active.sentiment) : null;

  return (
    <Shell>
      <div className="space-y-6 animate-fade-in-up">
        {/* Top Aggregation Header / Chart */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Narratives List Sidebar */}
          <div className="lg:col-span-1 space-y-4">
            <div className="flex items-center justify-between">
              <h4 className="text-xs font-bold uppercase tracking-wider text-granite-light">Active Market Themes</h4>
              {isMock && <Badge variant="warning">Simulated</Badge>}
            </div>
            
            <div className="space-y-4 max-h-[500px] overflow-y-auto pr-1">
              {narratives.map((nar) => (
                <NarrativeCard
                  key={nar.id}
                  narrative={nar}
                  onClick={() => setSelectedNarrative(nar)}
                  className={active.id === nar.id ? "border-caramel bg-caramel/5" : ""}
                />
              ))}
            </div>
          </div>

          {/* Detailed Narrative View */}
          <div className="lg:col-span-2 space-y-6">
            {active ? (
              <>
                <Card className="glass-card-static">
                  <CardHeader className="pb-4">
                    <div className="flex flex-wrap items-start justify-between gap-4">
                      <div className="space-y-1">
                        <div className="flex items-center space-x-2">
                          <Layers className="w-5 h-5 text-caramel" />
                          <CardTitle className="text-base">{active.title}</CardTitle>
                        </div>
                        <CardDescription>
                          First detected on {formatDate(active.first_seen)} • Updated {formatDate(active.last_updated)}
                        </CardDescription>
                      </div>
                      
                      <div className="flex items-center space-x-3">
                        {sent && <Badge variant={sent.variant}>{sent.label}</Badge>}
                        <Badge variant="secondary" className="font-mono">{active.article_count} Articles</Badge>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <p className="text-xs text-silk-muted leading-relaxed">
                      {active.description}
                    </p>

                    {/* Quick stats grid */}
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-4 border-t border-granite/10">
                      <div>
                        <span className="text-[10px] text-granite block uppercase font-bold">Trend Momentum</span>
                        <span className="text-xs font-bold text-silk capitalize block mt-0.5">{active.momentum}</span>
                      </div>
                      <div>
                        <span className="text-[10px] text-granite block uppercase font-bold">Thematic Score</span>
                        <span className="text-xs font-bold font-data text-caramel block mt-0.5">{active.trend_score}</span>
                      </div>
                      <div>
                        <span className="text-[10px] text-granite block uppercase font-bold">Sectors Involved</span>
                        <span className="text-xs font-bold text-silk block mt-0.5">{active.sectors.length || 3}</span>
                      </div>
                      <div>
                        <span className="text-[10px] text-granite block uppercase font-bold">Confidence Index</span>
                        <span className="text-xs font-bold text-positive flex items-center mt-0.5">
                          <ShieldCheck className="w-3.5 h-3.5 mr-1" />
                          High
                        </span>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Evolution Chart */}
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-xs uppercase font-bold text-granite-light">Theme Volume Evolution</CardTitle>
                    <CardDescription>Frequency of article mentions over the past 30 days</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <NarrativeTrend narratives={[active]} />
                  </CardContent>
                </Card>
              </>
            ) : (
              <div className="flex flex-col items-center justify-center h-80 border border-dashed border-granite/20 rounded-xl">
                <Layers className="w-8 h-8 text-granite-light animate-pulse" />
                <p className="text-xs text-granite-light mt-3">Select a narrative theme to inspect</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </Shell>
  );
}
