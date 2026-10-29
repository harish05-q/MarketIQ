"""Market Pulse dashboard Pydantic schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.article import ArticleSummary
from app.schemas.event import EventResponse
from app.schemas.narrative import NarrativeResponse


class SentimentDistribution(BaseModel):
    """Distribution of sentiment across recent articles."""

    very_bullish: int = 0
    bullish: int = 0
    neutral: int = 0
    bearish: int = 0
    very_bearish: int = 0
    total: int = 0


class SourceBreakdown(BaseModel):
    """Article count by source."""

    source: str
    count: int


class MarketPulseData(BaseModel):
    """Dashboard overview data aggregating key metrics."""

    total_articles: int = 0
    articles_today: int = 0
    average_sentiment_score: float = 0.0
    sentiment_distribution: SentimentDistribution = Field(default_factory=SentimentDistribution)
    source_breakdown: list[SourceBreakdown] = Field(default_factory=list)
    trending_narratives: list[NarrativeResponse] = Field(default_factory=list)
    recent_events: list[EventResponse] = Field(default_factory=list)
    top_articles: list[ArticleSummary] = Field(default_factory=list)
    last_ingestion: datetime | None = None


class MarketPulseResponse(BaseModel):
    """Standard market pulse API response."""

    success: bool = True
    data: MarketPulseData
