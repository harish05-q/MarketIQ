// ============================================
// MarketIQ - API Client
// ============================================

import type {
  Article,
  ArticleFilters,
  MarketPulse,
  Narrative,
  CompanyIntelligence,
  Briefing,
  Conversation,
  ChatMessage,
  ApiResponse,
  SearchSuggestion,
} from '@/types';

const API_BASE_URL = '/api/v1';

// --- Fetch Wrapper ---

async function apiFetch<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  const url = `${API_BASE_URL}${endpoint}`;

  const defaultHeaders: HeadersInit = {
    'Content-Type': 'application/json',
  };

  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers,
      },
    });

    if (!response.ok) {
      const errorBody = await response.text();
      throw new ApiError(
        `API Error: ${response.status} ${response.statusText}`,
        response.status,
        errorBody
      );
    }

    const data = await response.json();
    return data as ApiResponse<T>;
  } catch (error) {
    if (error instanceof ApiError) throw error;
    throw new ApiError(
      `Network Error: ${error instanceof Error ? error.message : 'Unknown error'}`,
      0
    );
  }
}

export class ApiError extends Error {
  status: number;
  body?: string;

  constructor(message: string, status: number, body?: string) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.body = body;
  }
}

// --- Query String Builder ---

function buildQueryString(params: Record<string, unknown>): string {
  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value === undefined || value === null) return;
    if (Array.isArray(value)) {
      value.forEach((v) => searchParams.append(key, String(v)));
    } else {
      searchParams.append(key, String(value));
    }
  });
  const qs = searchParams.toString();
  return qs ? `?${qs}` : '';
}

// ============================================
// API Endpoints
// ============================================

// --- Market Pulse ---

export async function fetchMarketPulse(): Promise<ApiResponse<MarketPulse>> {
  return apiFetch<MarketPulse>('/market-pulse');
}

// --- Articles ---

export async function fetchArticles(
  filters: ArticleFilters = {}
): Promise<ApiResponse<Article[]>> {
  const qs = buildQueryString(filters as Record<string, unknown>);
  return apiFetch<Article[]>(`/articles${qs}`);
}

export async function fetchArticleById(
  id: string
): Promise<ApiResponse<Article>> {
  return apiFetch<Article>(`/articles/${id}`);
}

// --- Narratives ---

export async function fetchNarratives(): Promise<ApiResponse<Narrative[]>> {
  return apiFetch<Narrative[]>('/narratives');
}

export async function fetchNarrativeById(
  id: string
): Promise<ApiResponse<Narrative>> {
  return apiFetch<Narrative>(`/narratives/${id}`);
}

// --- Companies ---

export async function fetchCompanyIntelligence(
  ticker: string
): Promise<ApiResponse<CompanyIntelligence>> {
  return apiFetch<CompanyIntelligence>(`/companies/${ticker}`);
}

export async function searchCompanies(
  query: string
): Promise<ApiResponse<SearchSuggestion[]>> {
  return apiFetch<SearchSuggestion[]>(`/companies/search?q=${encodeURIComponent(query)}`);
}

// --- Chat ---

export async function fetchConversations(): Promise<ApiResponse<Conversation[]>> {
  return apiFetch<Conversation[]>('/chat/conversations');
}

export async function fetchConversation(
  id: string
): Promise<ApiResponse<Conversation>> {
  return apiFetch<Conversation>(`/chat/conversations/${id}`);
}

export async function createConversation(): Promise<ApiResponse<Conversation>> {
  return apiFetch<Conversation>('/chat/conversations', {
    method: 'POST',
  });
}

export async function sendChatMessage(
  conversationId: string,
  message: string
): Promise<Response> {
  // Returns raw response for streaming
  const url = `${API_BASE_URL}/chat/conversations/${conversationId}/messages`;
  return fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message }),
  });
}

// --- Briefings ---

export async function fetchBriefings(
  type?: 'morning' | 'daily' | 'weekly'
): Promise<ApiResponse<Briefing[]>> {
  const qs = type ? `?type=${type}` : '';
  return apiFetch<Briefing[]>(`/briefings${qs}`);
}

export async function fetchLatestBriefing(
  type: 'morning' | 'daily' | 'weekly'
): Promise<ApiResponse<Briefing>> {
  return apiFetch<Briefing>(`/briefings/latest?type=${type}`);
}

// --- Search ---

export async function fetchSearchSuggestions(
  query: string
): Promise<ApiResponse<SearchSuggestion[]>> {
  return apiFetch<SearchSuggestion[]>(
    `/search/suggestions?q=${encodeURIComponent(query)}`
  );
}
