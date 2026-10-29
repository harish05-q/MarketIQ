"""Article repository with domain-specific query methods."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Sequence
from uuid import UUID

from sqlalchemy import and_, case, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import SentimentLabel
from app.core.logging import get_logger
from app.models.article import Article, ArticleEntity
from app.repositories.base import BaseRepository

logger = get_logger(__name__)


class ArticleRepository(BaseRepository[Article]):
    """Repository for Article CRUD and advanced queries."""

    model = Article

    async def get_by_source_url(self, source_url: str) -> Article | None:
        """Look up an article by its unique source URL.

        Args:
            source_url: The original article URL.

        Returns:
            Article instance or None if not found.
        """
        stmt = select(Article).where(Article.source_url == source_url)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def source_url_exists(self, source_url: str) -> bool:
        """Check if an article with the given source URL already exists.

        Args:
            source_url: The original article URL.

        Returns:
            True if an article with this URL is already stored.
        """
        stmt = select(func.count()).select_from(Article).where(Article.source_url == source_url)
        result = await self.session.execute(stmt)
        return result.scalar_one() > 0

    async def list_filtered(
        self,
        *,
        source: str | None = None,
        sentiment: str | None = None,
        sector: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        search: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[Sequence[Article], int]:
        """Return a filtered and paginated list of articles.

        Args:
            source: Filter by source name.
            sentiment: Filter by sentiment label.
            sector: Filter by sector entity (requires join).
            date_from: Minimum publication date (inclusive).
            date_to: Maximum publication date (inclusive).
            search: Full-text search on title.
            offset: Pagination offset.
            limit: Page size.

        Returns:
            Tuple of (articles, total_count).
        """
        conditions: list[Any] = []

        if source:
            conditions.append(Article.source == source)
        if sentiment:
            conditions.append(Article.sentiment == sentiment)
        if date_from:
            conditions.append(Article.published_at >= date_from)
        if date_to:
            conditions.append(Article.published_at <= date_to)
        if search:
            conditions.append(Article.title.ilike(f"%{search}%"))

        # Sector filter requires joining through entities
        base_stmt = select(Article)
        count_stmt = select(func.count()).select_from(Article)

        if sector:
            from app.models.entity import Entity
            base_stmt = base_stmt.join(ArticleEntity).join(Entity).where(
                and_(Entity.type == "sector", Entity.name.ilike(f"%{sector}%"))
            )
            count_stmt = count_stmt.join(ArticleEntity).join(Entity).where(
                and_(Entity.type == "sector", Entity.name.ilike(f"%{sector}%"))
            )

        if conditions:
            base_stmt = base_stmt.where(and_(*conditions))
            count_stmt = count_stmt.where(and_(*conditions))

        # Get total count
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar_one()

        # Get paginated results
        data_stmt = base_stmt.order_by(Article.published_at.desc().nullslast()).offset(offset).limit(limit)
        data_result = await self.session.execute(data_stmt)
        articles = data_result.scalars().all()

        return articles, total

    async def get_articles_since(self, since: datetime, limit: int = 100) -> Sequence[Article]:
        """Fetch articles published after a given timestamp.

        Args:
            since: Cutoff datetime.
            limit: Maximum articles to return.

        Returns:
            List of articles ordered by publication date descending.
        """
        stmt = (
            select(Article)
            .where(Article.published_at >= since)
            .order_by(Article.published_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_top_articles(self, limit: int = 10) -> Sequence[Article]:
        """Fetch top articles by impact score.

        Args:
            limit: Maximum articles to return.

        Returns:
            List of articles ordered by impact score descending.
        """
        stmt = (
            select(Article)
            .where(Article.impact_score.isnot(None))
            .order_by(Article.impact_score.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_sentiment_distribution(self) -> dict[str, int]:
        """Get the count of articles per sentiment label.

        Returns:
            Dictionary mapping sentiment labels to counts.
        """
        stmt = (
            select(Article.sentiment, func.count().label("count"))
            .where(Article.sentiment.isnot(None))
            .group_by(Article.sentiment)
        )
        result = await self.session.execute(stmt)
        return {row.sentiment: row.count for row in result}

    async def get_source_breakdown(self) -> list[dict[str, Any]]:
        """Get the count of articles per source.

        Returns:
            List of dicts with 'source' and 'count' keys.
        """
        stmt = (
            select(Article.source, func.count().label("count"))
            .group_by(Article.source)
            .order_by(func.count().desc())
        )
        result = await self.session.execute(stmt)
        return [{"source": row.source, "count": row.count} for row in result]

    async def get_average_sentiment_score(self) -> float:
        """Calculate the average sentiment score across all articles.

        Returns:
            Average sentiment score, or 0.0 if no scored articles exist.
        """
        stmt = select(func.avg(Article.sentiment_score)).where(Article.sentiment_score.isnot(None))
        result = await self.session.execute(stmt)
        avg = result.scalar_one_or_none()
        return float(avg) if avg is not None else 0.0

    async def get_articles_today_count(self) -> int:
        """Count articles published today.

        Returns:
            Integer count.
        """
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        stmt = select(func.count()).select_from(Article).where(Article.created_at >= today_start)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_last_ingestion_time(self) -> datetime | None:
        """Get the timestamp of the most recently created article.

        Returns:
            Datetime or None if no articles exist.
        """
        stmt = select(Article.created_at).order_by(Article.created_at.desc()).limit(1)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_articles_by_entity_name(
        self, entity_name: str, limit: int = 20
    ) -> Sequence[Article]:
        """Fetch articles associated with a specific entity name.

        Args:
            entity_name: Entity name to search for (case-insensitive).
            limit: Maximum results.

        Returns:
            List of articles linked to the entity.
        """
        from app.models.entity import Entity
        stmt = (
            select(Article)
            .join(ArticleEntity)
            .join(Entity)
            .where(Entity.name.ilike(f"%{entity_name}%"))
            .order_by(Article.published_at.desc().nullslast())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_articles_without_summary(self, limit: int = 50) -> Sequence[Article]:
        """Fetch articles that have not yet been summarized.

        Args:
            limit: Maximum results.

        Returns:
            List of un-summarized articles.
        """
        stmt = (
            select(Article)
            .where(Article.summary.is_(None))
            .order_by(Article.created_at.asc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_articles_without_sentiment(self, limit: int = 50) -> Sequence[Article]:
        """Fetch articles that have not been sentiment-analysed.

        Args:
            limit: Maximum results.

        Returns:
            List of articles without sentiment.
        """
        stmt = (
            select(Article)
            .where(Article.sentiment.is_(None))
            .order_by(Article.created_at.asc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
