"""Market Pulse dashboard service aggregating key metrics."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.repositories.article_repo import ArticleRepository
from app.repositories.event_repo import EventRepository
from app.repositories.narrative_repo import NarrativeRepository
from app.schemas.article import ArticleSummary
from app.schemas.event import EventResponse
from app.schemas.market_pulse import (
    MarketPulseData,
    SentimentDistribution,
    SourceBreakdown,
)
from app.schemas.narrative import NarrativeResponse

logger = get_logger(__name__)


class MarketPulseService:
    """Aggregates data from multiple repositories into a dashboard overview."""

    def __init__(self, session: AsyncSession) -> None:
        self.article_repo = ArticleRepository(session)
        self.event_repo = EventRepository(session)
        self.narrative_repo = NarrativeRepository(session)

    async def get_market_pulse(self) -> MarketPulseData:
        """Build the market pulse dashboard data.

        Returns:
            MarketPulseData with all aggregated metrics.
        """
        # Total articles
        total_articles = await self.article_repo.count()

        # Articles today
        articles_today = await self.article_repo.get_articles_today_count()

        # Average sentiment score
        avg_sentiment = await self.article_repo.get_average_sentiment_score()

        # Sentiment distribution
        sentiment_dist_raw = await self.article_repo.get_sentiment_distribution()
        sentiment_distribution = SentimentDistribution(
            very_bullish=sentiment_dist_raw.get("very_bullish", 0),
            bullish=sentiment_dist_raw.get("bullish", 0),
            neutral=sentiment_dist_raw.get("neutral", 0),
            bearish=sentiment_dist_raw.get("bearish", 0),
            very_bearish=sentiment_dist_raw.get("very_bearish", 0),
            total=sum(sentiment_dist_raw.values()) if sentiment_dist_raw else 0,
        )

        # Source breakdown
        source_raw = await self.article_repo.get_source_breakdown()
        source_breakdown = [
            SourceBreakdown(source=s["source"], count=s["count"])
            for s in source_raw
        ]

        # Trending narratives
        trending_raw = await self.narrative_repo.get_trending(limit=5)
        trending_narratives = [
            NarrativeResponse.model_validate(n) for n in trending_raw
        ]

        # Recent events
        recent_events_raw = await self.event_repo.get_recent_events(limit=10)
        recent_events = [
            EventResponse.model_validate(e) for e in recent_events_raw
        ]

        # Top articles by impact
        top_articles_raw = await self.article_repo.get_top_articles(limit=10)
        top_articles = [
            ArticleSummary.model_validate(a) for a in top_articles_raw
        ]

        # Last ingestion time
        last_ingestion = await self.article_repo.get_last_ingestion_time()

        return MarketPulseData(
            total_articles=total_articles,
            articles_today=articles_today,
            average_sentiment_score=round(avg_sentiment, 4),
            sentiment_distribution=sentiment_distribution,
            source_breakdown=source_breakdown,
            trending_narratives=trending_narratives,
            recent_events=recent_events,
            top_articles=top_articles,
            last_ingestion=last_ingestion,
        )
