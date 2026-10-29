"use client";

import * as React from "react";
import { Search, Filter, RefreshCw, X, ShieldAlert, Tag, Calendar, Sparkles } from "lucide-react";
import { Shell } from "@/components/layout/shell";
import { Card, CardContent, Input, Button, Badge } from "@/components/ui";
import { ArticleCard, formatDate, getSentimentDetails } from "@/components/cards";
import { fetchArticles } from "@/lib/api";
import { mockArticles } from "@/lib/mock-data";
import type { Article } from "@/types";

export default function NewsExplorerPage() {
  const [articles, setArticles] = React.useState<Article[]>([]);
  const [loading, setLoading] = React.useState<boolean>(true);
  const [isMock, setIsMock] = React.useState<boolean>(false);
  
  // Search & Filter state
  const [search, setSearch] = React.useState<string>("");
  const [selectedSource, setSelectedSource] = React.useState<string>("All");
  const [selectedSentiment, setSelectedSentiment] = React.useState<string>("All");
  
  // Detail Modal state
  const [selectedArticle, setSelectedArticle] = React.useState<Article | null>(null);

  // Fetch articles from API
  const loadArticles = React.useCallback(async () => {
    setLoading(true);
    try {
      const filters: any = {};
      if (search) filters.search = search;
      // Note: Backend takes string parameters, so we send simple filters
      const response = await fetchArticles(filters);
      if (response.status === "success" && response.data && response.data.length > 0) {
        // Backend returns raw Article Detail which matches the shape or needs mapping
        // We'll map backend to our local shapes
        const apiArticles = response.data.map((art: any) => ({
          id: art.id,
          title: art.title,
          summary: art.summary || "",
          content: art.content || "",
          url: art.source_url,
          source: art.source,
          published_at: art.published_at,
          scraped_at: art.created_at,
          sentiment: {
            score: art.sentiment_score || 0,
            label: art.sentiment?.toLowerCase() || "neutral",
            confidence: 0.9,
          },
          impact_score: art.impact_score || 50,
          entities: art.entities || [],
          sectors: art.metadata?.sectors || [],
          narratives: art.metadata?.narratives || [],
        }));
        setArticles(apiArticles);
        setIsMock(false);
      } else {
        throw new Error("Empty backend database");
      }
    } catch (err) {
      console.warn("API Offline or empty, using mock articles:", err);
      setArticles(mockArticles);
      setIsMock(true);
    } finally {
      setLoading(false);
    }
  }, [search]);

  React.useEffect(() => {
    loadArticles();
  }, [loadArticles]);

  // Extract unique sources and sectors for filters
  const sources = React.useMemo(() => {
    const s = new Set<string>();
    articles.forEach(a => s.add(a.source));
    return ["All", ...Array.from(s)];
  }, [articles]);

  const filteredArticles = React.useMemo(() => {
    return articles.filter(art => {
      const matchesSearch = search ? art.title.toLowerCase().includes(search.toLowerCase()) || art.summary.toLowerCase().includes(search.toLowerCase()) : true;
      const matchesSource = selectedSource === "All" ? true : art.source === selectedSource;
      const matchesSentiment = selectedSentiment === "All" ? true : art.sentiment.label.toLowerCase() === selectedSentiment.toLowerCase();
      return matchesSearch && matchesSource && matchesSentiment;
    });
  }, [articles, search, selectedSource, selectedSentiment]);

  return (
    <Shell>
      <div className="space-y-6">
        {/* Filter Controls Row */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-ash/40 p-4 border border-granite/10 rounded-xl glass-surface">
          {/* Search Input */}
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-granite-light" />
            <Input
              placeholder="Search news intelligence by headlines, tickers or tags..."
              className="pl-9 h-9"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>

          {/* Selector filters */}
          <div className="flex flex-wrap items-center gap-3">
            {/* Source dropdown */}
            <div className="flex items-center space-x-2">
              <span className="text-[10px] uppercase font-bold text-granite-light font-mono">Source:</span>
              <select
                className="bg-ash-deep border border-granite/20 text-silk text-xs rounded-md px-2 py-1.5 focus:outline-none focus:border-caramel"
                value={selectedSource}
                onChange={(e) => setSelectedSource(e.target.value)}
              >
                {sources.map(src => (
                  <option key={src} value={src}>{src}</option>
                ))}
              </select>
            </div>

            {/* Sentiment Filter */}
            <div className="flex items-center space-x-2">
              <span className="text-[10px] uppercase font-bold text-granite-light font-mono">Sentiment:</span>
              <div className="flex bg-ash-deep border border-granite/20 p-0.5 rounded-md">
                {["All", "Positive", "Neutral", "Negative"].map(sent => (
                  <button
                    key={sent}
                    onClick={() => setSelectedSentiment(sent)}
                    className={`px-2 py-1 rounded text-[10px] font-semibold transition-all ${
                      selectedSentiment === sent
                        ? "bg-caramel text-ash-deep font-bold"
                        : "text-granite-light hover:text-silk"
                    }`}
                  >
                    {sent}
                  </button>
                ))}
              </div>
            </div>

            <Button
              variant="ghost"
              size="icon"
              onClick={loadArticles}
              className="h-8 w-8 text-granite hover:text-silk"
              title="Reload Articles"
            >
              <RefreshCw className="w-3.5 h-3.5" />
            </Button>
          </div>
        </div>

        {/* Total Results and Mock banner */}
        <div className="flex items-center justify-between text-xs text-granite-light">
          <span>Showing <strong className="text-silk">{filteredArticles.length}</strong> matching articles</span>
          {isMock && <span className="text-caramel font-semibold">Simulated news source feed active</span>}
        </div>

        {/* Loading Indicator */}
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="h-44 skeleton" />
            ))}
          </div>
        ) : filteredArticles.length === 0 ? (
          /* Empty State */
          <div className="flex flex-col items-center justify-center py-20 border border-dashed border-granite/20 rounded-xl space-y-4">
            <ShieldAlert className="w-10 h-10 text-granite-light" />
            <div className="text-center space-y-1">
              <h4 className="font-bold text-sm text-silk">No articles matched your criteria</h4>
              <p className="text-xs text-granite-light">Try adjusting your filters or search keyword.</p>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                setSearch("");
                setSelectedSource("All");
                setSelectedSentiment("All");
              }}
            >
              Clear All Filters
            </Button>
          </div>
        ) : (
          /* Articles Grid */
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredArticles.map((art) => (
              <ArticleCard
                key={art.id}
                article={art}
                onClick={() => setSelectedArticle(art)}
              />
            ))}
          </div>
        )}

        {/* ─── Sidebar/Drawer Detail View ─── */}
        {selectedArticle && (
          <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex justify-end animate-fade-in">
            {/* Backdrop click closer */}
            <div className="flex-1" onClick={() => setSelectedArticle(null)} />

            {/* Sidebar content */}
            <div className="w-full max-w-xl bg-ash-deep border-l border-granite/10 flex flex-col h-full shadow-2xl relative animate-slide-in-right">
              {/* Header */}
              <div className="h-16 flex items-center justify-between px-6 border-b border-granite/10">
                <div className="flex items-center space-x-2 text-xs font-mono text-granite-light">
                  <span className="font-bold text-silk-muted">{selectedArticle.source}</span>
                  <span>•</span>
                  <span>{formatDate(selectedArticle.published_at)}</span>
                </div>
                <button
                  onClick={() => setSelectedArticle(null)}
                  className="p-1 text-granite-light hover:text-silk transition-colors rounded-lg bg-ash/50 border border-granite/10"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              {/* Scrollable details */}
              <div className="flex-1 overflow-y-auto p-6 space-y-6">
                {/* Title */}
                <h3 className="text-base font-bold text-silk leading-snug">
                  {selectedArticle.title}
                </h3>

                {/* Score stats grid */}
                <div className="grid grid-cols-3 gap-4 bg-ash/40 p-4 border border-granite/10 rounded-lg">
                  <div>
                    <span className="text-[9px] uppercase font-bold text-granite-light block">Sentiment</span>
                    <Badge variant={getSentimentDetails(selectedArticle.sentiment).variant} className="mt-1">
                      {getSentimentDetails(selectedArticle.sentiment).label}
                    </Badge>
                  </div>
                  <div>
                    <span className="text-[9px] uppercase font-bold text-granite-light block">Sentiment Score</span>
                    <span className="font-data font-semibold text-xs text-silk block mt-1">
                      {selectedArticle.sentiment.score.toFixed(2)}
                    </span>
                  </div>
                  <div>
                    <span className="text-[9px] uppercase font-bold text-granite-light block">Impact Index</span>
                    <span className="font-data font-semibold text-xs text-caramel block mt-1">
                      {Math.round(selectedArticle.impact_score)}
                    </span>
                  </div>
                </div>

                {/* AI Summary */}
                {selectedArticle.summary && (
                  <div className="space-y-2">
                    <div className="flex items-center space-x-1.5 text-caramel">
                      <Sparkles className="w-3.5 h-3.5" />
                      <h4 className="text-xs font-bold uppercase tracking-wider">AI Executive Summary</h4>
                    </div>
                    <p className="text-xs text-silk-muted leading-relaxed bg-ash/20 border border-granite/5 p-4 rounded-lg">
                      {selectedArticle.summary}
                    </p>
                  </div>
                )}

                {/* Full Article Content */}
                {selectedArticle.content && (
                  <div className="space-y-2">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-granite-light">Parsed Content Body</h4>
                    <div className="text-xs text-silk-muted leading-relaxed whitespace-pre-line space-y-3">
                      {selectedArticle.content}
                    </div>
                  </div>
                )}

                {/* Entities and Sectors Tag section */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 pt-4 border-t border-granite/10">
                  {/* Mentioned Entities */}
                  <div className="space-y-2">
                    <h5 className="text-[10px] font-bold uppercase tracking-wider text-granite">Extracted Entities</h5>
                    <div className="flex flex-wrap gap-1">
                      {selectedArticle.entities.length > 0 ? (
                        selectedArticle.entities.map((e, idx) => (
                          <span key={idx} className="text-[10px] font-mono text-caramel-warm bg-caramel/5 px-2 py-0.5 rounded border border-caramel/10">
                            {e.name}
                          </span>
                        ))
                      ) : (
                        <span className="text-[10px] text-granite-light italic">None detected</span>
                      )}
                    </div>
                  </div>

                  {/* Sectors */}
                  <div className="space-y-2">
                    <h5 className="text-[10px] font-bold uppercase tracking-wider text-granite">Affected Sectors</h5>
                    <div className="flex flex-wrap gap-1">
                      {selectedArticle.sectors && selectedArticle.sectors.length > 0 ? (
                        selectedArticle.sectors.map((s, idx) => (
                          <span key={idx} className="text-[10px] font-mono text-granite-light bg-ash-light/20 px-2 py-0.5 rounded border border-granite/10">
                            {s}
                          </span>
                        ))
                      ) : (
                        <span className="text-[10px] text-granite-light italic">None detected</span>
                      )}
                    </div>
                  </div>
                </div>
              </div>

              {/* Footer actions */}
              <div className="h-16 border-t border-granite/10 px-6 flex items-center justify-between bg-ash/20">
                {selectedArticle.url && (
                  <a
                    href={selectedArticle.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn-primary text-xs flex items-center space-x-2 px-4 py-2"
                  >
                    <span>View Original Source</span>
                    <RefreshCw className="w-3.5 h-3.5 -rotate-45" />
                  </a>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </Shell>
  );
}
