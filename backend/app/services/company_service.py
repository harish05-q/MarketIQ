"""Company service aggregating data about a specific company/ticker."""

from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.repositories.article_repo import ArticleRepository
from app.repositories.entity_repo import EntityRepository
from app.repositories.event_repo import EventRepository
from app.schemas.article import ArticleSummary
from app.schemas.event import EventResponse

logger = get_logger(__name__)


class CompanyService:
    """Aggregates articles, events, and entity data for a company ticker."""

    def __init__(self, session: AsyncSession) -> None:
        self.article_repo = ArticleRepository(session)
        self.entity_repo = EntityRepository(session)
        self.event_repo = EventRepository(session)

    async def get_company_profile(self, ticker: str) -> dict[str, Any]:
        """Build a company profile aggregating all related data.

        Args:
            ticker: Company ticker symbol or name.

        Returns:
            Dictionary containing company data: entity info, recent
            articles, related events, and sentiment summary.
        """
        # Find entity by ticker/name
        entity = await self.entity_repo.get_by_name_and_type(ticker.upper(), "company")
        entity_data = None
        if entity:
            entity_data = {
                "id": str(entity.id),
                "name": entity.name,
                "type": entity.type,
                "confidence": entity.confidence,
            }

        # Search for articles mentioning this ticker
        articles = await self.article_repo.get_articles_by_entity_name(ticker, limit=20)
        article_summaries = [ArticleSummary.model_validate(a) for a in articles]

        # Calculate sentiment stats from related articles
        sentiment_scores = [
            a.sentiment_score for a in articles
            if a.sentiment_score is not None
        ]
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0.0

        sentiment_counts: dict[str, int] = {}
        for a in articles:
            if a.sentiment:
                sentiment_counts[a.sentiment] = sentiment_counts.get(a.sentiment, 0) + 1

        # Get events mentioning this entity
        related_events: list[dict[str, Any]] = []
        for article in articles[:10]:
            if article.events:
                for event in article.events:
                    related_events.append(
                        EventResponse.model_validate(event).model_dump()
                    )

        return {
            "ticker": ticker.upper(),
            "entity": entity_data,
            "article_count": len(articles),
            "recent_articles": [a.model_dump() for a in article_summaries[:10]],
            "average_sentiment_score": round(avg_sentiment, 4),
            "sentiment_distribution": sentiment_counts,
            "recent_events": related_events[:10],
        }
