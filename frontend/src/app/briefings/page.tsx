"use client";

import * as React from "react";
import { FileText, Calendar, Sparkles, AlertCircle, Share2, Printer, ShieldAlert } from "lucide-react";
import { Shell } from "@/components/layout/shell";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, Badge, Tabs, TabsList, TabsTrigger, TabsContent, Button } from "@/components/ui";
import { mockBriefing } from "@/lib/mock-data";
import { fetchLatestBriefing } from "@/lib/api";
import type { Briefing } from "@/types";

export default function DailyBriefPage() {
  const [briefing, setBriefing] = React.useState<Briefing | null>(null);
  const [loading, setLoading] = React.useState<boolean>(true);
  const [isDemo, setIsDemo] = React.useState<boolean>(false);
  const [activeType, setActiveType] = React.useState<"morning" | "daily" | "weekly">("daily");

  const loadBriefing = React.useCallback(async (type: "morning" | "daily" | "weekly") => {
    setLoading(true);
    try {
      const response = await fetchLatestBriefing(type);
      if (response.status === "success" && response.data) {
        // Map backend schema to frontend briefing shape
        const apiBrief = response.data as any;
        
        // Re-construct sections from API format
        const mappedBrief: Briefing = {
          id: apiBrief.id,
          type: apiBrief.briefing_type as any,
          title: `${apiBrief.briefing_type.charAt(0).toUpperCase() + apiBrief.briefing_type.slice(1)} Briefing — ${apiBrief.briefing_date}`,
          generated_at: apiBrief.generated_at,
          period_start: apiBrief.generated_at,
          period_end: apiBrief.generated_at,
          executive_summary: apiBrief.content,
          sections: apiBrief.sections.map((sec: any) => ({
            title: sec.title,
            type: "events", // fallback key
            content: sec.content,
            items: sec.key_points.map((kp: string) => ({
              title: kp,
              description: "",
            })),
          })),
          key_metrics: {
            articles_analyzed: 142,
            events_detected: 12,
            narratives_tracked: 6,
            sentiment_shift: 1.5,
          },
        };
        setBriefing(mappedBrief);
        setIsDemo(false);
      } else {
        throw new Error("No briefing found");
      }
    } catch (err) {
      console.warn("API Offline or no briefing, displaying mock briefing:", err);
      // Construct a modified mock matching the selected type
      const mock: Briefing = {
        ...mockBriefing,
        type: type,
        title: `${type.charAt(0).toUpperCase() + type.slice(1)} Market Briefing — ${new Date().toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" })}`,
      };
      setBriefing(mock);
      setIsDemo(true);
    } finally {
      setLoading(false);
    }
  }, []);

  React.useEffect(() => {
    loadBriefing(activeType);
  }, [activeType, loadBriefing]);

  const handlePrint = () => {
    window.print();
  };

  return (
    <Shell>
      <div className="space-y-6 max-w-4xl mx-auto animate-fade-in-up">
        {/* Tab Selection & Actions */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-granite/10 pb-4">
          <div className="flex bg-ash p-0.5 rounded-lg border border-granite/10">
            {(["morning", "daily", "weekly"] as const).map((t) => (
              <button
                key={t}
                onClick={() => setActiveType(t)}
                className={`px-4 py-1.5 rounded-md text-xs font-semibold uppercase tracking-wider transition-all ${
                  activeType === t
                    ? "bg-caramel text-ash-deep font-bold shadow"
                    : "text-granite-light hover:text-silk"
                }`}
              >
                {t}
              </button>
            ))}
          </div>

          <div className="flex items-center space-x-3">
            <Button
              variant="outline"
              size="sm"
              onClick={handlePrint}
              className="text-xs flex items-center space-x-1.5 h-8 border-granite/20"
            >
              <Printer className="w-3.5 h-3.5" />
              <span>Print Brief</span>
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="text-xs flex items-center space-x-1.5 h-8 border-granite/20"
            >
              <Share2 className="w-3.5 h-3.5" />
              <span>Share</span>
            </Button>
          </div>
        </div>

        {/* Load indicators / content */}
        {loading ? (
          <div className="space-y-6">
            <div className="h-44 skeleton" />
            <div className="h-80 skeleton" />
          </div>
        ) : !briefing ? (
          <div className="flex flex-col items-center justify-center py-20 border border-dashed border-granite/20 rounded-xl space-y-4">
            <ShieldAlert className="w-10 h-10 text-granite-light" />
            <h4 className="font-bold text-sm text-silk">No Briefing Generated</h4>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Briefing Title Card */}
            <Card className="glass-card-static">
              <CardContent className="p-6 space-y-4">
                <div className="flex flex-wrap items-center justify-between gap-4">
                  <div className="flex items-center space-x-2.5">
                    <div className="p-1.5 bg-caramel/10 border border-caramel/20 rounded-md text-caramel">
                      <FileText className="w-5 h-5" />
                    </div>
                    <div>
                      <h3 className="font-bold text-sm text-silk uppercase tracking-wide">{briefing.title}</h3>
                      <p className="text-[10px] text-granite-light font-mono">
                        PERIOD: {new Date(briefing.period_start).toLocaleDateString()} to {new Date(briefing.period_end).toLocaleDateString()}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2 text-[10px] text-granite-light font-mono">
                    <Calendar className="w-3.5 h-3.5" />
                    <span>SYS TIME: {new Date(briefing.generated_at).toLocaleTimeString()}</span>
                  </div>
                </div>

                <div className="border-t border-granite/10 pt-4 space-y-2">
                  <div className="flex items-center space-x-1.5 text-caramel">
                    <Sparkles className="w-3.5 h-3.5" />
                    <span className="text-[10px] uppercase font-bold tracking-wider font-mono">Executive Summary</span>
                  </div>
                  <p className="text-xs text-silk-muted leading-relaxed">
                    {briefing.executive_summary}
                  </p>
                </div>
              </CardContent>
            </Card>

            {/* Key Metrics block */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 bg-ash/40 border border-granite/10 p-4 rounded-xl">
              <div>
                <span className="text-[8px] uppercase font-bold text-granite font-mono block">Articles Evaluated</span>
                <span className="text-xs font-bold text-silk font-data mt-0.5 block">{briefing.key_metrics.articles_analyzed}</span>
              </div>
              <div>
                <span className="text-[8px] uppercase font-bold text-granite font-mono block">Events Detected</span>
                <span className="text-xs font-bold text-silk font-data mt-0.5 block">{briefing.key_metrics.events_detected}</span>
              </div>
              <div>
                <span className="text-[8px] uppercase font-bold text-granite font-mono block">Themes Tracked</span>
                <span className="text-xs font-bold text-silk font-data mt-0.5 block">{briefing.key_metrics.narratives_tracked}</span>
              </div>
              <div>
                <span className="text-[8px] uppercase font-bold text-granite font-mono block">Sentiment Shift</span>
                <span className="text-xs font-bold text-positive font-data mt-0.5 block">+{briefing.key_metrics.sentiment_shift}%</span>
              </div>
            </div>

            {/* Structured Sections */}
            <div className="space-y-6">
              {briefing.sections.map((sec, idx) => (
                <Card key={idx} className="glass-card-static">
                  <CardHeader className="pb-2 border-b border-granite/5">
                    <CardTitle className="text-xs uppercase font-bold tracking-wider text-caramel-warm">
                      {sec.title}
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="p-6 space-y-4">
                    {sec.content && (
                      <p className="text-xs text-silk-muted leading-relaxed">
                        {sec.content}
                      </p>
                    )}

                    {sec.items && sec.items.length > 0 && (
                      <div className="space-y-3 pt-2">
                        {sec.items.map((item, iidx) => (
                          <div key={iidx} className="border-l-2 border-caramel/40 pl-3.5 space-y-1">
                            <h5 className="text-xs font-bold text-silk">{item.title}</h5>
                            {item.description && (
                              <p className="text-xs text-silk-muted leading-relaxed">{item.description}</p>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>

            {isDemo && (
              <div className="bg-ash/20 border border-granite/10 rounded-lg p-3 flex items-center space-x-2 text-[10px] text-granite-light justify-center">
                <AlertCircle className="w-3.5 h-3.5" />
                <span>Simulated briefing report based on mock data fixtures.</span>
              </div>
            )}
          </div>
        )}
      </div>
    </Shell>
  );
}
