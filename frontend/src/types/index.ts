// ============================================
// MarketIQ - Type Definitions
// ============================================

// --- Core Entities ---

export interface Entity {
  id: string;
  name: string;
  ticker?: string;
  type: 'company' | 'person' | 'sector' | 'index' | 'commodity' | 'currency';
  sector?: string;
  sentiment_score?: number;
  article_count?: number;
  logo_url?: string;
}

export interface SentimentData {
  score: number; // -1 to 1
  label: 'positive' | 'negative' | 'neutral';
  confidence: number; // 0 to 1
}

// --- Articles ---

export interface Article {
  id: string;
  title: string;
  summary: string;
  content?: string;
  url: string;
  source: string;
  source_logo?: string;
  published_at: string;
  scraped_at: string;
  sentiment: SentimentData;
  impact_score: number; // 0 to 100
  entities: Entity[];
  sectors: string[];
  narratives: string[];
  event_type?: string;
  image_url?: string;
}

export interface ArticleFilters {
  search?: string;
  sources?: string[];
  sentiment?: ('positive' | 'negative' | 'neutral')[];
  sectors?: string[];
  date_from?: string;
  date_to?: string;
  min_impact?: number;
  page?: number;
  page_size?: number;
  sort_by?: 'published_at' | 'impact_score' | 'sentiment';
  sort_order?: 'asc' | 'desc';
}

// --- Events ---

export interface Event {
  id: string;
  title: string;
  description: string;
  event_type: 'earnings' | 'merger' | 'regulation' | 'product_launch' | 'leadership' | 'market_move' | 'geopolitical' | 'other';
  severity: 'low' | 'medium' | 'high' | 'critical';
  confidence: number;
  timestamp: string;
  entities: Entity[];
  articles: string[]; // article IDs
  impact_score: number;
  sectors: string[];
}

// --- Narratives ---

export interface NarrativeDataPoint {
  date: string;
  frequency: number;
  sentiment: number;
}

export interface Narrative {
  id: string;
  title: string;
  description: string;
  trend_score: number; // -100 to 100
  momentum: 'rising' | 'falling' | 'stable';
  article_count: number;
  sentiment: SentimentData;
  sectors: string[];
  entities: Entity[];
  timeline: NarrativeDataPoint[];
  first_seen: string;
  last_updated: string;
  related_narratives?: string[];
}

// --- Market Pulse ---

export interface SectorSentiment {
  name: string;
  sentiment_score: number;
  article_count: number;
  trend: 'up' | 'down' | 'stable';
  change_24h: number;
}

export interface MarketPulse {
  overall_sentiment: SentimentData;
  sentiment_history: { date: string; score: number }[];
  top_companies: Entity[];
  sectors: SectorSentiment[];
  top_events: Event[];
  trending_narratives: Narrative[];
  activity_feed: ActivityFeedItem[];
  last_updated: string;
}

export interface ActivityFeedItem {
  id: string;
  type: 'article' | 'event' | 'narrative' | 'alert';
  title: string;
  description: string;
  timestamp: string;
  sentiment?: SentimentData;
  impact_score?: number;
  entity?: Entity;
}

// --- Company Intelligence ---

export interface CompanyIntelligence {
  entity: Entity;
  sentiment_history: { date: string; score: number; volume: number }[];
  recent_events: Event[];
  related_narratives: Narrative[];
  recent_articles: Article[];
  peer_comparison: Entity[];
  risk_signals: RiskSignal[];
}

export interface RiskSignal {
  id: string;
  type: string;
  severity: 'low' | 'medium' | 'high';
  description: string;
  timestamp: string;
}

// --- Chat / RAG ---

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
  timestamp: string;
  is_streaming?: boolean;
}

export interface Citation {
  id: string;
  article_id: string;
  title: string;
  source: string;
  url: string;
  relevance_score: number;
}

export interface Conversation {
  id: string;
  title: string;
  messages: ChatMessage[];
  created_at: string;
  updated_at: string;
}

// --- Briefings ---

export interface BriefingSection {
  title: string;
  type: 'events' | 'sentiment' | 'narratives' | 'risks' | 'companies';
  content: string;
  items: BriefingItem[];
}

export interface BriefingItem {
  title: string;
  description: string;
  sentiment?: SentimentData;
  impact_score?: number;
  entities?: Entity[];
}

export interface Briefing {
  id: string;
  type: 'morning' | 'daily' | 'weekly';
  title: string;
  generated_at: string;
  period_start: string;
  period_end: string;
  executive_summary: string;
  sections: BriefingSection[];
  key_metrics: {
    articles_analyzed: number;
    events_detected: number;
    narratives_tracked: number;
    sentiment_shift: number;
  };
}

// --- API Response ---

export interface ApiResponse<T> {
  data: T;
  status: 'success' | 'error';
  message?: string;
  pagination?: {
    page: number;
    page_size: number;
    total_items: number;
    total_pages: number;
  };
}

// --- Misc ---

export interface SearchSuggestion {
  text: string;
  type: 'company' | 'narrative' | 'sector' | 'query';
  entity_id?: string;
}
