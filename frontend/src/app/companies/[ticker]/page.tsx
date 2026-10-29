"use client";

import * as React from "react";
import Link from "next/link";
import { 
  Building2, Activity, Clock, Layers, ArrowLeft, AlertCircle, 
  Sparkles, TrendingUp, TrendingDown, ShieldAlert
} from "lucide-react";
import { Shell } from "@/components/layout/shell";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, Badge, Button } from "@/components/ui";
import { ArticleCard, EventCard, NarrativeCard, getSentimentDetails, formatDate } from "@/components/cards";
import { fetchCompanyIntelligence } from "@/lib/api";
import { mockCompanyIntelligence } from "@/lib/mock-data";
import type { CompanyIntelligence } from "@/types";

export default function CompanyIntelligencePage({ params }: { params: Promise<{ ticker: string }> }) {
  // Unwrap parameters
  const resolvedParams = React.use(params);
  const ticker = resolvedParams.ticker.toUpperCase();

  const [data, setData] = React.useState<CompanyIntelligence | null>(null);
  const [loading, setLoading] = React.useState<boolean>(true);
  const [isDemo, setIsDemo] = React.useState<boolean>(false);

  React.useEffect(() => {
    async function loadCompanyProfile() {
      setLoading(true);
      try {
        const response = await fetchCompanyIntelligence(ticker);
        if (response.status === "success" && response.data && response.data.entity) {
          // Map backend dictionary to frontend intelligence shape
          const apiData = response.data as any;
          const mappedData: CompanyIntelligence = {
            entity: {
              id: apiData.entity.id,
              name: apiData.entity.name,
              ticker: apiData.ticker,
              type: "company",
              sentiment_score: apiData.average_sentiment_score,
              article_count: apiData.article_count,
            },
            sentiment_history: [
              { date: "Previous Week", score: apiData.average_sentiment_score * 0.8, volume: 5 },
              { date: "Yesterday", score: apiData.average_sentiment_score * 0.9, volume: 10 },
              { date: "Today", score: apiData.average_sentiment_score, volume: apiData.article_count },
            ],
            recent_events: apiData.recent_events.map((e: any) => ({
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
            related_narratives: [],
            recent_articles: apiData.recent_articles.map((art: any) => ({
              id: art.id,
              title: art.title,
              summary: art.summary || "",
              source: art.source,
              url: art.source_url,
              published_at: art.published_at,
              scraped_at: art.created_at,
              sentiment: { score: art.sentiment_score || 0, label: art.sentiment || "neutral" } as any,
              impact_score: art.impact_score || 50,
              entities: [],
              sectors: [],
              narratives: [],
            })),
            peer_comparison: [],
            risk_signals: [],
          };
          setData(mappedData);
          setIsDemo(false);
        } else {
          throw new Error("Company not found in backend DB");
        }
      } catch (err) {
        console.warn("API Offline or company missing, falling back to AAPL mock profile:", err);
        // Customise mock profile to match requested ticker
        const mock: CompanyIntelligence = {
          ...mockCompanyIntelligence,
          entity: {
            ...mockCompanyIntelligence.entity,
            name: ticker === "AAPL" ? "Apple Inc." : ticker === "NVDA" ? "NVIDIA Corp." : `${ticker} Corporation`,
            ticker: ticker,
          }
        };
        setData(mock);
        setIsDemo(true);
      } finally {
        setLoading(false);
      }
    }
    loadCompanyProfile();
  }, [ticker]);

  if (loading) {
    return (
      <Shell>
        <div className="space-y-6">
          <div className="h-20 skeleton" />
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="h-80 skeleton lg:col-span-2" />
            <div className="h-80 skeleton" />
          </div>
        </div>
      </Shell>
    );
  }

  const profile = data || mockCompanyIntelligence;
  const sent = getSentimentDetails(profile.entity.sentiment_score || 0);

  return (
    <Shell>
      <div className="space-y-6 animate-fade-in-up">
        {/* Back Link */}
        <div className="flex items-center justify-between">
          <Link href="/news" className="flex items-center space-x-1.5 text-xs text-granite-light hover:text-caramel transition-colors">
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to News Explorer</span>
          </Link>
          {isDemo && <Badge variant="warning">Simulated profile</Badge>}
        </div>

        {/* Company profile header */}
        <Card className="glass-card-static">
          <CardContent className="p-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-6">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 rounded bg-caramel/10 border border-caramel/20 flex items-center justify-center text-caramel font-mono font-bold text-lg">
                  {ticker.slice(0, 3)}
                </div>
                <div>
                  <h3 className="font-bold text-base text-silk">{profile.entity.name}</h3>
                  <div className="flex items-center space-x-2 mt-1.5">
                    <Badge variant="secondary" className="font-mono text-[9px]">{profile.entity.ticker}</Badge>
                    <span className="text-[10px] text-granite-light font-mono capitalize">{profile.entity.type}</span>
                  </div>
                </div>
              </div>

              {/* Sentiment Overview box */}
              <div className="flex items-center space-x-6 border-t sm:border-t-0 sm:border-l border-granite/10 pt-4 sm:pt-0 sm:pl-6">
                <div>
                  <span className="text-[9px] uppercase font-bold text-granite-light block">Avg Sentiment</span>
                  <span className={`font-data font-semibold text-sm block mt-0.5 ${sent.colorClass}`}>
                    {(profile.entity.sentiment_score || 0).toFixed(2)}
                  </span>
                </div>
                <div>
                  <span className="text-[9px] uppercase font-bold text-granite-light block">Article Coverage</span>
                  <span className="font-data font-semibold text-sm text-silk block mt-0.5">
                    {profile.entity.article_count || 14}
                  </span>
                </div>
                <div>
                  <span className="text-[9px] uppercase font-bold text-granite-light block">Risk Outlook</span>
                  <Badge variant={profile.risk_signals.length > 0 ? "warning" : "default"} className="mt-0.5">
                    {profile.risk_signals.length > 0 ? "Elevated" : "Normal"}
                  </Badge>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Grid split */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Related Articles & Events */}
          <div className="lg:col-span-2 space-y-6">
            {/* Recent News */}
            <div className="space-y-4">
              <h4 className="text-xs font-bold uppercase tracking-wider text-granite-light">Recent Mentioned Intelligence</h4>
              {profile.recent_articles.length === 0 ? (
                <div className="flex flex-col items-center justify-center p-12 border border-dashed border-granite/20 rounded-xl">
                  <ShieldAlert className="w-8 h-8 text-granite-light" />
                  <p className="text-xs text-granite-light mt-2">No related articles found</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {profile.recent_articles.slice(0, 4).map((art) => (
                    <ArticleCard key={art.id} article={art} />
                  ))}
                </div>
              )}
            </div>

            {/* Event Timeline */}
            <div className="space-y-4">
              <h4 className="text-xs font-bold uppercase tracking-wider text-granite-light">Entity Event Log</h4>
              {profile.recent_events.length === 0 ? (
                <div className="flex flex-col items-center justify-center p-12 border border-dashed border-granite/20 rounded-xl">
                  <ShieldAlert className="w-8 h-8 text-granite-light" />
                  <p className="text-xs text-granite-light mt-2">No related events logged</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {profile.recent_events.slice(0, 4).map((evt) => (
                    <EventCard key={evt.id} event={evt} />
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Sidebar (Narratives & Risks) */}
          <div className="space-y-6">
            {/* Narratives participation */}
            <div className="space-y-4">
              <h4 className="text-xs font-bold uppercase tracking-wider text-granite-light">Participating Narratives</h4>
              {profile.related_narratives.length === 0 ? (
                <div className="p-4 border border-granite/10 rounded-lg text-xs text-granite-light bg-ash/20">
                  No active narratives linked to this ticker.
                </div>
              ) : (
                <div className="space-y-4">
                  {profile.related_narratives.map((nar) => (
                    <NarrativeCard key={nar.id} narrative={nar} />
                  ))}
                </div>
              )}
            </div>

            {/* Risk signals */}
            {profile.risk_signals.length > 0 && (
              <div className="space-y-4">
                <h4 className="text-xs font-bold uppercase tracking-wider text-granite-light">Alert Signals & Risks</h4>
                <div className="space-y-3">
                  {profile.risk_signals.map((rs) => (
                    <div key={rs.id} className="p-4 bg-negative/5 border border-negative/20 rounded-lg space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-[10px] uppercase font-bold text-negative font-mono flex items-center">
                          <AlertCircle className="w-3.5 h-3.5 mr-1" />
                          {rs.type} Risk
                        </span>
                        <span className="text-[9px] text-granite font-mono">{formatDate(rs.timestamp)}</span>
                      </div>
                      <p className="text-xs text-silk-muted leading-relaxed">{rs.description}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </Shell>
  );
}
