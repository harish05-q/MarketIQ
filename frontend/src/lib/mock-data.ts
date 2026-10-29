// ============================================
// MarketIQ - Mock Data for Development
// ============================================

import type {
  Article,
  Entity,
  Event,
  Narrative,
  NarrativeDataPoint,
  MarketPulse,
  SectorSentiment,
  ActivityFeedItem,
  CompanyIntelligence,
  Briefing,
  Conversation,
  ChatMessage,
  Citation,
  RiskSignal,
} from '@/types';

// --- Entities ---

export const mockEntities: Entity[] = [
  { id: 'e1', name: 'Apple Inc.', ticker: 'AAPL', type: 'company', sector: 'Technology', sentiment_score: 0.72, article_count: 145 },
  { id: 'e2', name: 'NVIDIA Corporation', ticker: 'NVDA', type: 'company', sector: 'Technology', sentiment_score: 0.85, article_count: 203 },
  { id: 'e3', name: 'Tesla Inc.', ticker: 'TSLA', type: 'company', sector: 'Automotive', sentiment_score: -0.15, article_count: 178 },
  { id: 'e4', name: 'JPMorgan Chase', ticker: 'JPM', type: 'company', sector: 'Finance', sentiment_score: 0.45, article_count: 92 },
  { id: 'e5', name: 'Microsoft Corporation', ticker: 'MSFT', type: 'company', sector: 'Technology', sentiment_score: 0.68, article_count: 167 },
  { id: 'e6', name: 'Amazon.com Inc.', ticker: 'AMZN', type: 'company', sector: 'Technology', sentiment_score: 0.52, article_count: 134 },
  { id: 'e7', name: 'Alphabet Inc.', ticker: 'GOOGL', type: 'company', sector: 'Technology', sentiment_score: 0.38, article_count: 156 },
  { id: 'e8', name: 'Meta Platforms', ticker: 'META', type: 'company', sector: 'Technology', sentiment_score: 0.28, article_count: 112 },
];

// --- Articles ---

export const mockArticles: Article[] = [
  {
    id: 'a1',
    title: 'NVIDIA Reports Record Q4 Revenue Driven by AI Chip Demand',
    summary: 'NVIDIA\'s quarterly revenue surged 265% year-over-year to $22.1 billion, exceeding analyst expectations as data center demand for AI accelerators continues to skyrocket.',
    url: 'https://example.com/nvidia-q4',
    source: 'Reuters',
    published_at: new Date(Date.now() - 2 * 3600000).toISOString(),
    scraped_at: new Date().toISOString(),
    sentiment: { score: 0.89, label: 'positive', confidence: 0.95 },
    impact_score: 92,
    entities: [mockEntities[1]],
    sectors: ['Technology', 'Semiconductors'],
    narratives: ['AI Infrastructure Boom'],
    event_type: 'earnings',
  },
  {
    id: 'a2',
    title: 'Federal Reserve Signals Potential Rate Cuts in Late 2025',
    summary: 'Fed Chair Jerome Powell indicated the central bank may begin cutting interest rates if inflation continues to moderate, sending markets higher in afternoon trading.',
    url: 'https://example.com/fed-rates',
    source: 'Bloomberg',
    published_at: new Date(Date.now() - 5 * 3600000).toISOString(),
    scraped_at: new Date().toISOString(),
    sentiment: { score: 0.65, label: 'positive', confidence: 0.88 },
    impact_score: 88,
    entities: [],
    sectors: ['Finance', 'Macroeconomic'],
    narratives: ['Monetary Policy Shift'],
    event_type: 'regulation',
  },
  {
    id: 'a3',
    title: 'Tesla Faces Regulatory Scrutiny Over Autopilot Safety Claims',
    summary: 'NHTSA has opened a new investigation into Tesla\'s Full Self-Driving software following reports of multiple incidents on highways, potentially impacting the company\'s autonomous driving timeline.',
    url: 'https://example.com/tesla-autopilot',
    source: 'Wall Street Journal',
    published_at: new Date(Date.now() - 8 * 3600000).toISOString(),
    scraped_at: new Date().toISOString(),
    sentiment: { score: -0.62, label: 'negative', confidence: 0.91 },
    impact_score: 75,
    entities: [mockEntities[2]],
    sectors: ['Automotive', 'Technology'],
    narratives: ['Autonomous Driving Regulation'],
    event_type: 'regulation',
  },
  {
    id: 'a4',
    title: 'Apple Vision Pro Sales Exceed Expectations in Asian Markets',
    summary: 'Apple\'s spatial computing device saw stronger-than-expected adoption in Japan, South Korea, and China, with enterprise use cases driving bulk orders.',
    url: 'https://example.com/apple-vision-pro',
    source: 'Financial Times',
    published_at: new Date(Date.now() - 12 * 3600000).toISOString(),
    scraped_at: new Date().toISOString(),
    sentiment: { score: 0.58, label: 'positive', confidence: 0.85 },
    impact_score: 67,
    entities: [mockEntities[0]],
    sectors: ['Technology', 'Consumer Electronics'],
    narratives: ['Spatial Computing'],
    event_type: 'product_launch',
  },
  {
    id: 'a5',
    title: 'JPMorgan Expands AI Trading Platform with New LLM Integration',
    summary: 'JPMorgan Chase announces a major upgrade to its proprietary trading platform, incorporating large language models for real-time market analysis and trade execution.',
    url: 'https://example.com/jpm-ai-trading',
    source: 'CNBC',
    published_at: new Date(Date.now() - 16 * 3600000).toISOString(),
    scraped_at: new Date().toISOString(),
    sentiment: { score: 0.55, label: 'positive', confidence: 0.82 },
    impact_score: 62,
    entities: [mockEntities[3]],
    sectors: ['Finance', 'Technology'],
    narratives: ['AI in Finance'],
    event_type: 'product_launch',
  },
  {
    id: 'a6',
    title: 'Microsoft Azure Revenue Growth Accelerates on AI Workloads',
    summary: 'Microsoft reported 30% cloud revenue growth driven by a surge in enterprise AI deployments on Azure, outpacing AWS and Google Cloud.',
    url: 'https://example.com/msft-azure',
    source: 'Reuters',
    published_at: new Date(Date.now() - 20 * 3600000).toISOString(),
    scraped_at: new Date().toISOString(),
    sentiment: { score: 0.75, label: 'positive', confidence: 0.93 },
    impact_score: 78,
    entities: [mockEntities[4]],
    sectors: ['Technology', 'Cloud Computing'],
    narratives: ['Cloud AI Arms Race'],
    event_type: 'earnings',
  },
  {
    id: 'a7',
    title: 'Global Semiconductor Shortage Shows Signs of Easing',
    summary: 'New fab capacity coming online in Taiwan and Arizona is beginning to address supply bottlenecks that have constrained chip production for over two years.',
    url: 'https://example.com/chip-shortage',
    source: 'Bloomberg',
    published_at: new Date(Date.now() - 24 * 3600000).toISOString(),
    scraped_at: new Date().toISOString(),
    sentiment: { score: 0.42, label: 'positive', confidence: 0.78 },
    impact_score: 55,
    entities: [],
    sectors: ['Semiconductors', 'Manufacturing'],
    narratives: ['Supply Chain Recovery'],
    event_type: 'market_move',
  },
  {
    id: 'a8',
    title: 'Amazon Announces Major Layoffs in Cloud Division Restructuring',
    summary: 'Amazon plans to cut approximately 8,000 positions in its AWS division as part of a broader cost optimization strategy, focusing on efficiency over headcount growth.',
    url: 'https://example.com/amzn-layoffs',
    source: 'Wall Street Journal',
    published_at: new Date(Date.now() - 28 * 3600000).toISOString(),
    scraped_at: new Date().toISOString(),
    sentiment: { score: -0.45, label: 'negative', confidence: 0.87 },
    impact_score: 70,
    entities: [mockEntities[5]],
    sectors: ['Technology', 'Cloud Computing'],
    narratives: ['Tech Industry Restructuring'],
    event_type: 'leadership',
  },
];

// --- Events ---

export const mockEvents: Event[] = [
  {
    id: 'ev1',
    title: 'NVIDIA Q4 Earnings Beat',
    description: 'NVIDIA reported Q4 revenue of $22.1B, beating consensus estimates by 12%. Data center revenue up 409% YoY.',
    event_type: 'earnings',
    severity: 'critical',
    confidence: 0.97,
    timestamp: new Date(Date.now() - 2 * 3600000).toISOString(),
    entities: [mockEntities[1]],
    articles: ['a1'],
    impact_score: 92,
    sectors: ['Technology', 'Semiconductors'],
  },
  {
    id: 'ev2',
    title: 'Fed Rate Cut Signal',
    description: 'Federal Reserve Chair signals potential rate cuts by end of year, conditional on inflation trajectory.',
    event_type: 'regulation',
    severity: 'high',
    confidence: 0.88,
    timestamp: new Date(Date.now() - 5 * 3600000).toISOString(),
    entities: [],
    articles: ['a2'],
    impact_score: 88,
    sectors: ['Finance', 'Macroeconomic'],
  },
  {
    id: 'ev3',
    title: 'Tesla NHTSA Investigation',
    description: 'NHTSA opens formal investigation into Tesla FSD safety following multiple reported highway incidents.',
    event_type: 'regulation',
    severity: 'high',
    confidence: 0.91,
    timestamp: new Date(Date.now() - 8 * 3600000).toISOString(),
    entities: [mockEntities[2]],
    articles: ['a3'],
    impact_score: 75,
    sectors: ['Automotive'],
  },
  {
    id: 'ev4',
    title: 'Apple Vision Pro Asia Launch',
    description: 'Apple Vision Pro exceeds sales expectations in Japan, South Korea, and China markets.',
    event_type: 'product_launch',
    severity: 'medium',
    confidence: 0.85,
    timestamp: new Date(Date.now() - 12 * 3600000).toISOString(),
    entities: [mockEntities[0]],
    articles: ['a4'],
    impact_score: 67,
    sectors: ['Technology'],
  },
  {
    id: 'ev5',
    title: 'Amazon AWS Restructuring',
    description: 'Amazon announces 8,000 job cuts in AWS division as part of cost optimization strategy.',
    event_type: 'leadership',
    severity: 'high',
    confidence: 0.87,
    timestamp: new Date(Date.now() - 28 * 3600000).toISOString(),
    entities: [mockEntities[5]],
    articles: ['a8'],
    impact_score: 70,
    sectors: ['Technology', 'Cloud Computing'],
  },
];

// --- Narratives ---

function generateTimeline(days: number, baseFreq: number, trend: number): NarrativeDataPoint[] {
  const points: NarrativeDataPoint[] = [];
  for (let i = days; i >= 0; i--) {
    const date = new Date(Date.now() - i * 86400000);
    const noise = (Math.random() - 0.5) * 8;
    const freq = Math.max(0, baseFreq + trend * (days - i) + noise);
    const sentNoise = (Math.random() - 0.5) * 0.3;
    points.push({
      date: date.toISOString().split('T')[0],
      frequency: Math.round(freq),
      sentiment: Math.max(-1, Math.min(1, 0.3 + sentNoise + trend * 0.01 * (days - i))),
    });
  }
  return points;
}

export const mockNarratives: Narrative[] = [
  {
    id: 'n1',
    title: 'AI Infrastructure Boom',
    description: 'Massive investment in AI compute infrastructure driving semiconductor and cloud stocks. NVIDIA, AMD, and cloud providers seeing unprecedented demand for AI-capable hardware.',
    trend_score: 87,
    momentum: 'rising',
    article_count: 342,
    sentiment: { score: 0.78, label: 'positive', confidence: 0.92 },
    sectors: ['Technology', 'Semiconductors', 'Cloud Computing'],
    entities: [mockEntities[1], mockEntities[4]],
    timeline: generateTimeline(30, 15, 0.8),
    first_seen: new Date(Date.now() - 90 * 86400000).toISOString(),
    last_updated: new Date().toISOString(),
  },
  {
    id: 'n2',
    title: 'Monetary Policy Shift',
    description: 'Growing expectations of central bank rate cuts across major economies as inflation moderates. Bond markets and rate-sensitive sectors repricing accordingly.',
    trend_score: 65,
    momentum: 'rising',
    article_count: 228,
    sentiment: { score: 0.55, label: 'positive', confidence: 0.85 },
    sectors: ['Finance', 'Real Estate', 'Macroeconomic'],
    entities: [mockEntities[3]],
    timeline: generateTimeline(30, 12, 0.5),
    first_seen: new Date(Date.now() - 60 * 86400000).toISOString(),
    last_updated: new Date().toISOString(),
  },
  {
    id: 'n3',
    title: 'Autonomous Driving Regulation',
    description: 'Increasing regulatory pressure on autonomous vehicle companies as safety concerns mount. NHTSA and European regulators tightening oversight.',
    trend_score: -32,
    momentum: 'rising',
    article_count: 156,
    sentiment: { score: -0.42, label: 'negative', confidence: 0.88 },
    sectors: ['Automotive', 'Technology', 'Regulation'],
    entities: [mockEntities[2]],
    timeline: generateTimeline(30, 8, 0.3),
    first_seen: new Date(Date.now() - 45 * 86400000).toISOString(),
    last_updated: new Date().toISOString(),
  },
  {
    id: 'n4',
    title: 'Cloud AI Arms Race',
    description: 'Major cloud providers racing to offer AI-as-a-service capabilities. Microsoft Azure, AWS, and Google Cloud competing for enterprise AI workloads.',
    trend_score: 72,
    momentum: 'stable',
    article_count: 189,
    sentiment: { score: 0.62, label: 'positive', confidence: 0.86 },
    sectors: ['Technology', 'Cloud Computing'],
    entities: [mockEntities[4], mockEntities[5], mockEntities[6]],
    timeline: generateTimeline(30, 10, 0.4),
    first_seen: new Date(Date.now() - 75 * 86400000).toISOString(),
    last_updated: new Date().toISOString(),
  },
  {
    id: 'n5',
    title: 'Tech Industry Restructuring',
    description: 'Major technology companies implementing significant workforce reductions and cost optimization measures. Focus shifting from growth to profitability.',
    trend_score: -18,
    momentum: 'falling',
    article_count: 134,
    sentiment: { score: -0.28, label: 'negative', confidence: 0.82 },
    sectors: ['Technology'],
    entities: [mockEntities[5], mockEntities[7]],
    timeline: generateTimeline(30, 12, -0.3),
    first_seen: new Date(Date.now() - 120 * 86400000).toISOString(),
    last_updated: new Date().toISOString(),
  },
  {
    id: 'n6',
    title: 'Spatial Computing',
    description: 'The emergence of spatial computing as a new platform paradigm led by Apple Vision Pro. Enterprise and consumer adoption patterns taking shape.',
    trend_score: 45,
    momentum: 'rising',
    article_count: 98,
    sentiment: { score: 0.48, label: 'positive', confidence: 0.79 },
    sectors: ['Technology', 'Consumer Electronics'],
    entities: [mockEntities[0], mockEntities[7]],
    timeline: generateTimeline(30, 5, 0.6),
    first_seen: new Date(Date.now() - 30 * 86400000).toISOString(),
    last_updated: new Date().toISOString(),
  },
];

// --- Sector Sentiments ---

export const mockSectorSentiments: SectorSentiment[] = [
  { name: 'Technology', sentiment_score: 0.65, article_count: 892, trend: 'up', change_24h: 3.2 },
  { name: 'Finance', sentiment_score: 0.42, article_count: 445, trend: 'up', change_24h: 1.8 },
  { name: 'Healthcare', sentiment_score: 0.18, article_count: 312, trend: 'stable', change_24h: -0.3 },
  { name: 'Energy', sentiment_score: -0.12, article_count: 267, trend: 'down', change_24h: -2.1 },
  { name: 'Consumer', sentiment_score: 0.35, article_count: 389, trend: 'up', change_24h: 0.9 },
  { name: 'Industrial', sentiment_score: 0.22, article_count: 198, trend: 'stable', change_24h: 0.1 },
  { name: 'Real Estate', sentiment_score: -0.08, article_count: 156, trend: 'down', change_24h: -1.4 },
  { name: 'Automotive', sentiment_score: -0.25, article_count: 223, trend: 'down', change_24h: -3.5 },
  { name: 'Semiconductors', sentiment_score: 0.78, article_count: 367, trend: 'up', change_24h: 4.1 },
  { name: 'Cloud Computing', sentiment_score: 0.58, article_count: 298, trend: 'up', change_24h: 2.3 },
  { name: 'Crypto/Blockchain', sentiment_score: 0.12, article_count: 178, trend: 'stable', change_24h: 0.5 },
  { name: 'Biotech', sentiment_score: 0.32, article_count: 145, trend: 'up', change_24h: 1.2 },
];

// --- Activity Feed ---

export const mockActivityFeed: ActivityFeedItem[] = [
  {
    id: 'af1', type: 'event', title: 'NVIDIA Q4 Earnings Beat',
    description: 'Revenue surged 265% YoY to $22.1B', timestamp: new Date(Date.now() - 120000).toISOString(),
    sentiment: { score: 0.89, label: 'positive', confidence: 0.95 }, impact_score: 92,
    entity: mockEntities[1],
  },
  {
    id: 'af2', type: 'article', title: 'Fed Signals Rate Cuts Ahead',
    description: 'Markets rally on dovish commentary', timestamp: new Date(Date.now() - 600000).toISOString(),
    sentiment: { score: 0.65, label: 'positive', confidence: 0.88 }, impact_score: 88,
  },
  {
    id: 'af3', type: 'narrative', title: 'AI Infrastructure Boom trend accelerating',
    description: 'Narrative score increased by +12 in 24h', timestamp: new Date(Date.now() - 1800000).toISOString(),
    sentiment: { score: 0.78, label: 'positive', confidence: 0.92 },
  },
  {
    id: 'af4', type: 'alert', title: 'Tesla sentiment drop detected',
    description: 'TSLA sentiment fell below -0.5 threshold', timestamp: new Date(Date.now() - 3600000).toISOString(),
    sentiment: { score: -0.62, label: 'negative', confidence: 0.91 }, impact_score: 75,
    entity: mockEntities[2],
  },
  {
    id: 'af5', type: 'article', title: 'Microsoft Azure AI Revenue Surges',
    description: '30% cloud growth driven by enterprise AI', timestamp: new Date(Date.now() - 5400000).toISOString(),
    sentiment: { score: 0.75, label: 'positive', confidence: 0.93 }, impact_score: 78,
    entity: mockEntities[4],
  },
  {
    id: 'af6', type: 'event', title: 'Apple Vision Pro Expansion',
    description: 'Strong adoption in Asian markets', timestamp: new Date(Date.now() - 7200000).toISOString(),
    sentiment: { score: 0.58, label: 'positive', confidence: 0.85 }, impact_score: 67,
    entity: mockEntities[0],
  },
];

// --- Market Pulse ---

function generateSentimentHistory(days: number): { date: string; score: number }[] {
  const result: { date: string; score: number }[] = [];
  let score = 0.3;
  for (let i = days; i >= 0; i--) {
    const date = new Date(Date.now() - i * 86400000);
    score += (Math.random() - 0.48) * 0.08;
    score = Math.max(-0.5, Math.min(0.8, score));
    result.push({ date: date.toISOString().split('T')[0], score: parseFloat(score.toFixed(3)) });
  }
  return result;
}

export const mockMarketPulse: MarketPulse = {
  overall_sentiment: { score: 0.42, label: 'positive', confidence: 0.87 },
  sentiment_history: generateSentimentHistory(30),
  top_companies: mockEntities.slice(0, 5),
  sectors: mockSectorSentiments,
  top_events: mockEvents,
  trending_narratives: mockNarratives.slice(0, 4),
  activity_feed: mockActivityFeed,
  last_updated: new Date().toISOString(),
};

// --- Company Intelligence (AAPL example) ---

export const mockCompanyIntelligence: CompanyIntelligence = {
  entity: mockEntities[0],
  sentiment_history: Array.from({ length: 30 }, (_, i) => {
    const date = new Date(Date.now() - (29 - i) * 86400000);
    return {
      date: date.toISOString().split('T')[0],
      score: 0.5 + Math.sin(i * 0.3) * 0.3 + (Math.random() - 0.5) * 0.1,
      volume: Math.floor(30 + Math.random() * 50),
    };
  }),
  recent_events: mockEvents.filter(e => e.entities.some(en => en.ticker === 'AAPL')),
  related_narratives: mockNarratives.filter(n => n.entities.some(en => en.ticker === 'AAPL')),
  recent_articles: mockArticles.filter(a => a.entities.some(en => en.ticker === 'AAPL')),
  peer_comparison: mockEntities.filter(e => e.sector === 'Technology').slice(0, 4),
  risk_signals: [
    { id: 'rs1', type: 'regulatory', severity: 'medium', description: 'EU DMA compliance deadline approaching', timestamp: new Date().toISOString() },
    { id: 'rs2', type: 'competition', severity: 'low', description: 'Samsung XR headset launch may impact Vision Pro market share', timestamp: new Date().toISOString() },
  ] as RiskSignal[],
};

// --- Briefings ---

export const mockBriefing: Briefing = {
  id: 'b1',
  type: 'morning',
  title: 'Morning Market Brief — June 20, 2026',
  generated_at: new Date().toISOString(),
  period_start: new Date(Date.now() - 86400000).toISOString(),
  period_end: new Date().toISOString(),
  executive_summary: 'Markets are showing broad-based optimism driven by strong tech earnings and dovish Fed signals. AI infrastructure spending continues to dominate narratives, with NVIDIA\'s record quarter setting the tone. Key risks include regulatory scrutiny in autonomous driving and continued tech workforce restructuring.',
  sections: [
    {
      title: 'Top Events',
      type: 'events',
      content: 'Five high-impact events detected in the last 24 hours, predominantly in Technology and Finance sectors.',
      items: [
        { title: 'NVIDIA Q4 Earnings Beat', description: 'Revenue surged 265% YoY to $22.1B, exceeding consensus by 12%.', sentiment: { score: 0.89, label: 'positive', confidence: 0.95 }, impact_score: 92 },
        { title: 'Fed Rate Cut Signal', description: 'Federal Reserve Chair signals potential rate cuts by year-end.', sentiment: { score: 0.65, label: 'positive', confidence: 0.88 }, impact_score: 88 },
        { title: 'Tesla NHTSA Investigation', description: 'New formal investigation into FSD safety claims.', sentiment: { score: -0.62, label: 'negative', confidence: 0.91 }, impact_score: 75 },
      ],
    },
    {
      title: 'Market Sentiment',
      type: 'sentiment',
      content: 'Overall market sentiment is moderately positive at +42, up from +38 yesterday. Technology and Semiconductors lead sector sentiment.',
      items: [
        { title: 'Technology', description: 'Sentiment score: +65, trending up with strong AI narrative support.' },
        { title: 'Semiconductors', description: 'Sentiment score: +78, highest sector sentiment driven by NVIDIA earnings.' },
        { title: 'Automotive', description: 'Sentiment score: -25, pressured by Tesla regulatory concerns.' },
      ],
    },
    {
      title: 'Emerging Narratives',
      type: 'narratives',
      content: 'Three narratives showing significant momentum changes in the last 24 hours.',
      items: [
        { title: 'AI Infrastructure Boom', description: 'Trend score: +87, accelerating. NVIDIA earnings reinforce narrative momentum.' },
        { title: 'Monetary Policy Shift', description: 'Trend score: +65, rising. Fed commentary driving increased coverage.' },
        { title: 'Spatial Computing', description: 'Trend score: +45, rising. Apple Vision Pro Asian expansion fueling optimism.' },
      ],
    },
    {
      title: 'Risk Signals',
      type: 'risks',
      content: 'Two elevated risk signals detected across monitored entities.',
      items: [
        { title: 'Regulatory Risk — Tesla', description: 'NHTSA investigation could delay FSD rollout. Impact on TSLA sentiment trajectory.', sentiment: { score: -0.62, label: 'negative', confidence: 0.91 }, impact_score: 75 },
        { title: 'Workforce Risk — Amazon', description: 'AWS layoffs signal potential revenue headwinds in cloud division.', sentiment: { score: -0.45, label: 'negative', confidence: 0.87 }, impact_score: 70 },
      ],
    },
    {
      title: 'Key Companies',
      type: 'companies',
      content: 'Top companies by impact and sentiment change in the reporting period.',
      items: [
        { title: 'NVDA — NVIDIA', description: 'Sentiment: +85 (▲), 203 articles. Record earnings driving strong positive coverage.' },
        { title: 'TSLA — Tesla', description: 'Sentiment: -15 (▼), 178 articles. Regulatory scrutiny weighing on sentiment.' },
        { title: 'MSFT — Microsoft', description: 'Sentiment: +68 (▲), 167 articles. Azure AI growth narrative strengthening.' },
      ],
    },
  ],
  key_metrics: {
    articles_analyzed: 1247,
    events_detected: 23,
    narratives_tracked: 18,
    sentiment_shift: 4.2,
  },
};

// --- Conversations ---

export const mockConversations: Conversation[] = [
  {
    id: 'c1',
    title: 'AI chip market analysis',
    messages: [],
    created_at: new Date(Date.now() - 3600000).toISOString(),
    updated_at: new Date(Date.now() - 1800000).toISOString(),
  },
  {
    id: 'c2',
    title: 'Fed rate impact on tech',
    messages: [],
    created_at: new Date(Date.now() - 86400000).toISOString(),
    updated_at: new Date(Date.now() - 43200000).toISOString(),
  },
  {
    id: 'c3',
    title: 'Tesla regulatory outlook',
    messages: [],
    created_at: new Date(Date.now() - 172800000).toISOString(),
    updated_at: new Date(Date.now() - 86400000).toISOString(),
  },
];

export const mockChatMessages: ChatMessage[] = [
  {
    id: 'cm1',
    role: 'user',
    content: 'What is the current sentiment around NVIDIA and the AI chip market?',
    timestamp: new Date(Date.now() - 300000).toISOString(),
  },
  {
    id: 'cm2',
    role: 'assistant',
    content: `Based on my analysis of **203 recent articles**, NVIDIA (NVDA) currently has the **strongest positive sentiment** among all tracked companies, with a sentiment score of **+85**.

## Key Findings

1. **Record Q4 Earnings**: NVIDIA reported revenue of $22.1 billion, a 265% increase year-over-year, significantly beating analyst expectations [1].

2. **AI Infrastructure Demand**: The primary driver is unprecedented demand for AI accelerators in data centers. The "AI Infrastructure Boom" narrative has a trend score of +87 and is accelerating [2].

3. **Market Position**: NVIDIA maintains dominant market share in AI training chips, with the H100 and upcoming B100 chips seeing strong pre-orders from major cloud providers [3].

## Sentiment Breakdown
- **Positive articles**: 78% (159 articles)
- **Neutral articles**: 18% (37 articles)  
- **Negative articles**: 4% (7 articles)

The negative coverage primarily relates to supply constraints and high valuation concerns, though these are minor compared to the overwhelmingly bullish narrative.

## Risk Factors
- Supply chain constraints for advanced packaging
- Potential export restrictions to China
- Valuation concerns at current price levels`,
    citations: [
      { id: 'cit1', article_id: 'a1', title: 'NVIDIA Reports Record Q4 Revenue', source: 'Reuters', url: '#', relevance_score: 0.95 },
      { id: 'cit2', article_id: 'a6', title: 'Microsoft Azure Revenue Growth Accelerates', source: 'Reuters', url: '#', relevance_score: 0.82 },
      { id: 'cit3', article_id: 'a7', title: 'Global Semiconductor Shortage Shows Signs of Easing', source: 'Bloomberg', url: '#', relevance_score: 0.75 },
    ] as Citation[],
    timestamp: new Date(Date.now() - 298000).toISOString(),
  },
];

// --- Suggested Questions ---

export const suggestedQuestions = [
  'What are the key drivers behind NVIDIA\'s recent earnings beat?',
  'How might Fed rate cuts impact the technology sector?',
  'What risks does Tesla face from NHTSA\'s Autopilot investigation?',
  'Compare sentiment across major cloud providers (AWS, Azure, GCP)',
  'What emerging narratives should I watch this week?',
  'Analyze the impact of AI infrastructure spending on semiconductor stocks',
];
