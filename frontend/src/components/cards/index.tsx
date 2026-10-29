import * as React from "react";
import Link from "next/link";
import { 
  TrendingUp, TrendingDown, Clock, Link as LinkIcon, AlertTriangle, 
  Layers, Users, Star, BarChart3, Activity, ArrowUpRight
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Card, CardContent, Badge } from "@/components/ui";
import type { Article, Event, Narrative, Entity } from "@/types";

// Helper to format date
export function formatDate(dateString?: string): string {
  if (!dateString) return "N/A";
  try {
    const d = new Date(dateString);
    return d.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return dateString;
  }
}

// Helper to get sentiment label & style
export function getSentimentDetails(score?: number | string | { score: number }) {
  let val = 0;
  if (typeof score === "number") {
    val = score;
  } else if (score && typeof score === "object" && "score" in score) {
    val = score.score;
  } else if (typeof score === "string") {
    const parsed = parseFloat(score);
    if (!isNaN(parsed)) val = parsed;
    else if (score.toLowerCase() === "positive" || score.toLowerCase() === "bullish") val = 0.5;
    else if (score.toLowerCase() === "negative" || score.toLowerCase() === "bearish") val = -0.5;
  }

  if (val > 0.15) {
    return {
      label: val > 0.5 ? "Very Bullish" : "Bullish",
      variant: "positive" as const,
      colorClass: "text-positive",
      bgClass: "bg-positive/10",
      icon: <TrendingUp className="w-3.5 h-3.5 mr-1" />,
    };
  } else if (val < -0.15) {
    return {
      label: val < -0.5 ? "Very Bearish" : "Bearish",
      variant: "negative" as const,
      colorClass: "text-negative",
      bgClass: "bg-negative/10",
      icon: <TrendingDown className="w-3.5 h-3.5 mr-1" />,
    };
  } else {
    return {
      label: "Neutral",
      variant: "neutral" as const,
      colorClass: "text-neutral-sent",
      bgClass: "bg-neutral-sent/10",
      icon: <Activity className="w-3.5 h-3.5 mr-1" />,
    };
  }
}

// --- 1. ArticleCard ---
export interface ArticleCardProps {
  article: Partial<Article> & { title: string; source: string };
  onClick?: () => void;
  className?: string;
}

export function ArticleCard({ article: rawArticle, onClick, className }: ArticleCardProps) {
  const article = rawArticle as any;
  const sent = getSentimentDetails(article.sentiment_score ?? article.sentiment);
  
  return (
    <Card 
      onClick={onClick}
      className={cn(
        "group cursor-pointer hover:border-caramel/30 transition-all duration-300", 
        className
      )}
    >
      <CardContent className="p-5 flex flex-col justify-between h-full space-y-4">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div className="flex items-center space-x-2 text-xs text-granite-light">
            <span className="font-semibold text-silk-muted">{article.source}</span>
            <span>•</span>
            <div className="flex items-center">
              <Clock className="w-3 h-3 mr-1" />
              <span>{formatDate(article.published_at)}</span>
            </div>
          </div>
          
          {/* Impact Score */}
          {article.impact_score !== undefined && (
            <div className="text-right">
              <span className="text-[10px] uppercase font-bold text-granite block leading-none">Impact</span>
              <span className="font-data font-semibold text-sm text-caramel leading-none block mt-0.5">
                {Math.round(article.impact_score)}
              </span>
            </div>
          )}
        </div>

        {/* Title & Summary */}
        <div className="space-y-2 flex-1">
          <h4 className="text-sm font-semibold text-silk group-hover:text-caramel transition-colors line-clamp-2 leading-snug">
            {article.title}
          </h4>
          {article.summary && (
            <p className="text-xs text-silk-muted line-clamp-2 leading-relaxed">
              {article.summary}
            </p>
          )}
        </div>

        {/* Footer info (Badges) */}
        <div className="flex items-center justify-between pt-2 border-t border-granite/10 text-xs">
          <Badge variant={sent.variant} className="flex items-center py-0.5">
            {sent.icon}
            {sent.label}
          </Badge>

          {article.source_url && (
            <a 
              href={article.source_url} 
              target="_blank" 
              rel="noopener noreferrer"
              onClick={(e) => e.stopPropagation()}
              className="text-granite-light hover:text-caramel transition-colors p-1"
            >
              <LinkIcon className="w-3.5 h-3.5" />
            </a>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

// --- 2. EventCard ---
export interface EventCardProps {
  event: Partial<Event> & { event_type: string; severity: string; confidence: number };
  onClick?: () => void;
  className?: string;
}

export function EventCard({ event, onClick, className }: EventCardProps) {
  const getSeverityStyle = (sev: string) => {
    switch (sev.toLowerCase()) {
      case "critical":
        return "border-negative/30 bg-negative/5 text-negative";
      case "high":
        return "border-warning/30 bg-warning/5 text-warning";
      case "medium":
        return "border-caramel/30 bg-caramel/5 text-caramel";
      default:
        return "border-granite/30 bg-granite/5 text-granite-light";
    }
  };

  const getEventName = (type: string) => {
    return type
      .replace(/_/g, " ")
      .replace(/\b\w/g, (char) => char.toUpperCase());
  };

  return (
    <Card 
      onClick={onClick}
      className={cn(
        "hover:border-caramel/20 transition-all duration-300", 
        onClick && "cursor-pointer",
        className
      )}
    >
      <CardContent className="p-4 space-y-3">
        {/* Title Line */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="w-1.5 h-1.5 rounded-full bg-caramel animate-pulse-glow" />
            <h5 className="font-semibold text-xs text-silk">
              {getEventName(event.event_type)}
            </h5>
          </div>
          <Badge className={cn("text-[10px] px-2 py-0.5 capitalize", getSeverityStyle(event.severity))}>
            {event.severity}
          </Badge>
        </div>

        {/* Description / Summary */}
        {event.description && (
          <p className="text-xs text-silk-muted line-clamp-2">
            {event.description}
          </p>
        )}

        {/* Affected Entities / Sectors */}
        <div className="flex flex-wrap gap-1 items-center">
          {event.entities?.slice(0, 3).map((ent, idx) => (
            <span key={idx} className="text-[10px] font-mono text-caramel-warm bg-caramel/5 px-1.5 py-0.5 rounded border border-caramel/10">
              {typeof ent === "string" ? ent : (ent as Entity).name}
            </span>
          ))}
          {event.sectors?.slice(0, 2).map((sec, idx) => (
            <span key={idx} className="text-[10px] font-mono text-granite-light bg-ash-light/20 px-1.5 py-0.5 rounded border border-granite/10">
              {sec}
            </span>
          ))}
        </div>

        {/* Footer status */}
        <div className="flex items-center justify-between pt-2 border-t border-granite/5 text-[10px] text-granite-light font-mono">
          <div className="flex items-center">
            <Clock className="w-3 h-3 mr-1" />
            <span>{formatDate(event.timestamp)}</span>
          </div>
          <div>
            <span>Conf: {(event.confidence * 100).toFixed(0)}%</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// --- 3. NarrativeCard ---
export interface NarrativeCardProps {
  narrative: Partial<Narrative> & { title: string; article_count: number; trend_score: number };
  onClick?: () => void;
  className?: string;
}

export function NarrativeCard({ narrative, onClick, className }: NarrativeCardProps) {
  const sent = getSentimentDetails(narrative.sentiment);
  const trendArrow = narrative.trend_score > 50 ? (
    <TrendingUp className="w-4 h-4 text-positive" />
  ) : narrative.trend_score < 20 ? (
    <TrendingDown className="w-4 h-4 text-negative" />
  ) : (
    <Activity className="w-4 h-4 text-caramel" />
  );

  return (
    <Card 
      onClick={onClick}
      className={cn(
        "group cursor-pointer hover:border-caramel/30 transition-all duration-300", 
        className
      )}
    >
      <CardContent className="p-5 flex flex-col justify-between h-full space-y-4">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div className="flex items-center space-x-1.5">
            <Layers className="w-3.5 h-3.5 text-caramel" />
            <span className="text-xs text-granite-light font-mono">Theme Narrative</span>
          </div>
          <Badge variant="secondary" className="font-mono text-[10px]">
            {narrative.article_count} articles
          </Badge>
        </div>

        {/* Content */}
        <div className="space-y-2 flex-1">
          <h4 className="text-sm font-semibold text-silk group-hover:text-caramel transition-colors line-clamp-1 leading-snug">
            {narrative.title}
          </h4>
          {narrative.description && (
            <p className="text-xs text-silk-muted line-clamp-2 leading-relaxed">
              {narrative.description}
            </p>
          )}
        </div>

        {/* Footer statistics */}
        <div className="flex items-center justify-between pt-3 border-t border-granite/10 text-xs">
          <div className="flex items-center space-x-1">
            <span className="text-[10px] text-granite uppercase font-bold block">Trend Index</span>
            <span className="font-data font-semibold text-silk block bg-ash/60 px-1.5 py-0.5 rounded border border-granite/5">
              {Math.round(narrative.trend_score)}
            </span>
            {trendArrow}
          </div>

          <Badge variant={sent.variant} className="py-0 flex items-center">
            {sent.icon}
            {sent.label}
          </Badge>
        </div>
      </CardContent>
    </Card>
  );
}

// --- 4. CompanyCard ---
export interface CompanyCardProps {
  company: Entity & { average_sentiment_score?: number; article_count?: number };
  className?: string;
}

export function CompanyCard({ company, className }: CompanyCardProps) {
  const sent = getSentimentDetails(company.average_sentiment_score ?? company.sentiment_score ?? 0);
  
  return (
    <Link href={`/companies/${company.name.toLowerCase()}`} className="block">
      <Card className={cn("hover:border-caramel/30 transition-all duration-300", className)}>
        <CardContent className="p-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded bg-caramel/10 border border-caramel/20 flex items-center justify-center text-caramel font-mono font-bold text-xs">
              {company.name.slice(0, 3).toUpperCase()}
            </div>
            <div>
              <div className="flex items-center space-x-1.5">
                <h5 className="font-bold text-xs text-silk">{company.name}</h5>
                <ArrowUpRight className="w-3 h-3 text-granite opacity-0 group-hover:opacity-100 transition-opacity" />
              </div>
              <p className="text-[10px] text-granite-light font-mono capitalize">{company.type}</p>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <div className="text-right">
              <span className="text-[9px] uppercase font-bold text-granite block">Sentiment</span>
              <span className={cn("font-data font-semibold text-xs leading-none block mt-0.5", sent.colorClass)}>
                {(company.average_sentiment_score ?? company.sentiment_score ?? 0).toFixed(2)}
              </span>
            </div>
            
            {company.article_count !== undefined && (
              <div className="text-right border-l border-granite/10 pl-3">
                <span className="text-[9px] uppercase font-bold text-granite block">Volume</span>
                <span className="font-data font-semibold text-xs text-silk block mt-0.5">
                  {company.article_count}
                </span>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}

// --- 5. StatCard ---
export interface StatCardProps {
  title: string;
  value: string | number;
  change?: number; // percentage change, e.g. 5.2
  timePeriod?: string;
  icon?: React.ReactNode;
  className?: string;
}

export function StatCard({ title, value, change, timePeriod = "from yesterday", icon, className }: StatCardProps) {
  const isPositive = change && change > 0;
  
  return (
    <Card className={cn("glass-card-static", className)}>
      <CardContent className="p-5 flex flex-col justify-between h-full space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-granite-light">{title}</span>
          <div className="p-1.5 bg-ash-light/20 border border-granite/10 rounded-md text-caramel">
            {icon || <Activity className="w-4 h-4" />}
          </div>
        </div>
        
        <div>
          <h3 className="text-2xl font-bold font-data text-silk tracking-tight leading-none">
            {value}
          </h3>
        </div>

        {change !== undefined && (
          <div className="flex items-center text-[10px] space-x-1.5 pt-1.5 border-t border-granite/5">
            <span className={cn(
              "font-semibold flex items-center font-mono",
              isPositive ? "text-positive" : "text-negative"
            )}>
              {isPositive ? <TrendingUp className="w-3 h-3 mr-0.5" /> : <TrendingDown className="w-3 h-3 mr-0.5" />}
              {isPositive ? "+" : ""}{change.toFixed(1)}%
            </span>
            <span className="text-granite-light font-medium">{timePeriod}</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
