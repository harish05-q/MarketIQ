"""Narrative repository."""

from __future__ import annotations

from typing import Sequence
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.narrative import Narrative
from app.repositories.base import BaseRepository

logger = get_logger(__name__)


class NarrativeRepository(BaseRepository[Narrative]):
    """Repository for Narrative CRUD and trending queries."""

    model = Narrative

    async def get_by_title(self, title: str) -> Narrative | None:
        """Find a narrative by its unique title.

        Args:
            title: Narrative title.

        Returns:
            Narrative instance or None.
        """
        stmt = select(Narrative).where(func.lower(Narrative.title) == title.lower())
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_or_create(self, title: str, description: str | None = None) -> Narrative:
        """Find an existing narrative or create a new one.

        Args:
            title: Narrative title.
            description: Optional description.

        Returns:
            The existing or newly created Narrative.
        """
        existing = await self.get_by_title(title)
        if existing is not None:
            return existing

        narrative = Narrative(title=title, description=description)
        return await self.create(narrative)

    async def list_paginated(
        self,
        *,
        trending: bool = False,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[Sequence[Narrative], int]:
        """Return a paginated list of narratives, optionally sorted by trend score.

        Args:
            trending: If True, sort by trend_score descending.
            offset: Pagination offset.
            limit: Page size.

        Returns:
            Tuple of (narratives, total_count).
        """
        # Count
        count_stmt = select(func.count()).select_from(Narrative)
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar_one()

        # Data
        data_stmt = select(Narrative)
        if trending:
            data_stmt = data_stmt.order_by(Narrative.trend_score.desc())
        else:
            data_stmt = data_stmt.order_by(Narrative.last_updated.desc())
        data_stmt = data_stmt.offset(offset).limit(limit)

        result = await self.session.execute(data_stmt)
        narratives = result.scalars().all()

        return narratives, total

    async def get_trending(self, limit: int = 5) -> Sequence[Narrative]:
        """Fetch the top trending narratives by trend score.

        Args:
            limit: Maximum narratives to return.

        Returns:
            List of top-trending narratives.
        """
        stmt = (
            select(Narrative)
            .order_by(Narrative.trend_score.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_active_narratives(self, min_articles: int = 3) -> Sequence[Narrative]:
        """Fetch narratives with at least a minimum number of associated articles.

        Args:
            min_articles: Minimum article_count threshold.

        Returns:
            Active narratives.
        """
        stmt = (
            select(Narrative)
            .where(Narrative.article_count >= min_articles)
            .order_by(Narrative.last_updated.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
