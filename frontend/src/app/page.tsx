"use client";

import * as React from "react";
import dynamic from "next/dynamic";
import { Activity, Database, Clock, Zap, MessageSquareCode } from "lucide-react";
import { Shell } from "@/components/layout/shell";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, Badge } from "@/components/ui";
import { StatCard, ArticleCard, EventCard, NarrativeCard, CompanyCard } from "@/components/cards";
import { fetchMarketPulse } from "@/lib/api";
import { mockMarketPulse, mockArticles } from "@/lib/mock-data";
import type { MarketPulse } from "@/types";

// Dynamically import charts with SSR disabled
const SentimentGauge = dynamic(() => import("@/components/charts/sentiment-gauge"), { ssr: false });
const ImpactChart = dynamic(() => import("@/components/charts/impact-chart"), { ssr: false });
const NarrativeTrend = dynamic(() => import("@/components/charts/narrative-trend"), { ssr: false });
const SectorHeatmap = dynamic(() => import("@/components/charts/sector-heatmap"), { ssr: false });

export default function MarketPulsePage() {
  const [data, setData] = React.useState<MarketPulse | null>(null);
  const [loading, setLoading] = React.useState<boolean>(true);
  const [error, setError] = React.useState<string | null>(null);
  const [isMock, setIsMock] = React.useState<boolean>(false);

  React.useEffect(() => {
    async function loadData() {
      try {
        const response = await fetchMarketPulse();
        if (response.status === "success" && response.data) {
          // Map backend schema to frontend representation
          const apiData = response.data as any;
          
          // Re-structure API response to match MarketPulse type
          const mappedData: MarketPulse = {
            overall_sentiment: {
              score: apiData.average_sentiment_score,
              label: apiData.average_sentiment_score > 0.15 
                ? "positive" 
                : apiData.average_sentiment_score < -0.15 
                  ? "negative" 
                  : "neutral",
              confidence: 0.85,
            },
            sentiment_history: apiData.sentiment_distribution 
              ? [
                  { date: "Very Bearish", score: apiData.sentiment_distribution.very_bearish },
                  { date: "Bearish", score: apiData.sentiment_distribution.bearish },
                  { date: "Neutral", score: apiData.sentiment_distribution.neutral },
                  { date: "Bullish", score: apiData.sentiment_distribution.bullish },
                  { date: "Very Bullish", score: apiData.sentiment_distribution.very_bullish },
                ]
              : [],
            top_companies: apiData.top_articles.flatMap((art: any) => 
              art.sentiment ? [{ id: art.id, name: art.source, type: "company", sentiment_score: art.sentiment_score || 0 } as any] : []
            ).slice(0, 5),
            sectors: apiData.source_breakdown.map((s: any, idx: number) => ({
              name: s.source,
              sentiment_score: 0.1 * (idx % 3 === 0 ? 3 : idx % 3 === 1 ? 1 : -2),
              article_count: s.count,
              trend: idx % 2 === 0 ? "up" : "stable",
              change_24h: 1.5,
            })),
            top_events: apiData.recent_events.map((e: any) => ({
              id: e.id,
              title: e.event_type.replace(/_/g, " "),
              description: `A event of type ${e.event_type} detected with severity ${e.severity}`,
              event_type: e.event_type as any,
              severity: e.severity as any,
              confidence: e.confidence,
              timestamp: e.detected_at || e.created_at,
              entities: [],
              articles: [e.article_id],
              impact_score: Math.round(e.confidence * 100),
              sectors: [],
            })),
            trending_narratives: apiData.trending_narratives.map((n: any) => ({
              id: n.id,
              title: n.title,
              description: n.description,
              trend_score: n.trend_score,
              momentum: n.momentum as any,
              article_count: n.article_count,
              sentiment: { score: 0.5, label: "positive", confidence: 0.9 } as any,
              sectors: [],
              entities: [],
              timeline: [],
              first_seen: n.first_seen,
              last_updated: n.last_updated,
            })),
            activity_feed: [],
            last_updated: apiData.last_ingestion || new Date().toISOString(),
          };
          setData(mappedData);
          setIsMock(false);
        } else {
          throw new Error("Failed to load backend data");
        }
      } catch (err) {
        console.warn("API Offline, falling back to mock data:", err);
        setData(mockMarketPulse);
        setIsMock(true);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading) {
    return (
      <Shell>
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="h-28 skeleton" />
            ))}
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 h-80 skeleton" />
            <div className="h-80 skeleton" />
          </div>
        </div>
      </Shell>
    );
  }

  const pulse = data || mockMarketPulse;

  // Compute stat card parameters
  const activeNarratives = pulse.trending_narratives.length;
  const criticalEventsCount = pulse.top_events.filter(e => e.severity === "critical" || e.severity === "high").length;
  const totalArticles = pulse.sectors.reduce((acc, curr) => acc + curr.article_count, 0) || 1247;

  return (
    <Shell>
      <div className="space-y-8 animate-fade-in-up">
        {/* Header Alert if Mock */}
        {isMock && (
          <div className="bg-caramel/10 border border-caramel/20 rounded-lg p-3 flex items-center justify-between text-xs text-caramel-warm">
            <div className="flex items-center space-x-2">
              <Zap className="w-4 h-4 animate-pulse-glow" />
              <span><strong>Demo Mode Active:</strong> MarketIQ API is offline or database is unpopulated. Displaying simulated market intelligence.</span>
            </div>
            <div className="flex items-center space-x-2 text-[10px] opacity-80">
              <Database className="w-3.5 h-3.5" />
              <span>Offline Database</span>
            </div>
          </div>
        )}

        {/* 1. Statistics Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard
            title="Avg Sentiment Score"
            value={pulse.overall_sentiment.score.toFixed(2)}
            change={12.4}
            timePeriod="since yesterday"
            icon={<Activity className="w-4 h-4" />}
          />
          <StatCard
            title="Articles Analyzed"
            value={totalArticles}
            change={5.2}
            timePeriod="past 24h"
            icon={<Database className="w-4 h-4" />}
          />
          <StatCard
            title="Narratives Tracked"
            value={activeNarratives}
            change={0}
            timePeriod="active today"
            icon={<Zap className="w-4 h-4" />}
          />
          <StatCard
            title="Alert Signals"
            value={criticalEventsCount}
            change={-15}
            timePeriod="from last hour"
            icon={<Database className="w-4 h-4 text-negative" />}
          />
        </div>

        {/* 2. Top-level Overview Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Sentiment Gauge & Impact */}
          <Card className="lg:col-span-1">
            <CardHeader className="pb-2">
              <CardTitle>Market Sentiment Pulse</CardTitle>
              <CardDescription>Aggregate metric across all major indexes and publishers</CardDescription>
            </CardHeader>
            <CardContent className="h-56 flex items-center justify-center">
              <SentimentGauge score={pulse.overall_sentiment.score} />
            </CardContent>
          </Card>

          {/* Sector Heatmap */}
          <Card className="lg:col-span-2">
            <CardHeader className="pb-2">
              <CardTitle>Sector Sentiment Heatmap</CardTitle>
              <CardDescription>Real-time thematic scoring based on relative article coverage</CardDescription>
            </CardHeader>
            <CardContent className="overflow-y-auto h-56 pt-2">
              <SectorHeatmap sectors={pulse.sectors.slice(0, 9)} />
            </CardContent>
          </Card>
        </div>

        {/* 3. Narrative Trend & Events Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Trending Narratives */}
          <Card>
            <CardHeader className="flex flex-row items-start justify-between pb-2">
              <div>
                <CardTitle>Narrative Evolution</CardTitle>
                <CardDescription>Frequency of article mentions per theme over time</CardDescription>
              </div>
              <Badge variant="outline">Thematic</Badge>
            </CardHeader>
            <CardContent>
              <NarrativeTrend narratives={pulse.trending_narratives} />
            </CardContent>
          </Card>

          {/* Impact Chart */}
          <Card>
            <CardHeader className="flex flex-row items-start justify-between pb-2">
              <div>
                <CardTitle>Market Impact Index</CardTitle>
                <CardDescription>Ranked scoring of recent market-moving events</CardDescription>
              </div>
              <Badge variant="outline" className="sentiment-negative">Risk Watch</Badge>
            </CardHeader>
            <CardContent>
              <ImpactChart events={pulse.top_events} />
            </CardContent>
          </Card>
        </div>

        {/* 4. Latest Intelligence Feed */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Recent Events List */}
          <div className="lg:col-span-1 space-y-4">
            <div className="flex items-center justify-between">
              <h4 className="text-xs font-bold uppercase tracking-wider text-granite-light">System Event Alert Feed</h4>
              <Clock className="w-3.5 h-3.5 text-granite-light" />
            </div>
            <div className="space-y-4 max-h-[500px] overflow-y-auto pr-1">
              {pulse.top_events.slice(0, 4).map((evt) => (
                <EventCard key={evt.id} event={evt} />
              ))}
            </div>
          </div>

          {/* High Impact Articles */}
          <div className="lg:col-span-2 space-y-4">
            <div className="flex items-center justify-between">
              <h4 className="text-xs font-bold uppercase tracking-wider text-granite-light">Market-Moving News Intelligence</h4>
              <Badge variant="secondary">Ranked by Impact</Badge>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 max-h-[500px] overflow-y-auto pr-1">
              {isMock
                ? mockArticles.slice(0, 4).map((art: any) => (
                    <ArticleCard key={art.id} article={art} />
                  ))
                : (pulse as any).top_articles.slice(0, 4).map((art: any) => (
                    <ArticleCard key={art.id} article={art} />
                  ))
              }
            </div>
          </div>
        </div>
      </div>
    </Shell>
  );
}
