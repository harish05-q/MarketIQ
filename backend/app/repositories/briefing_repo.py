"""Briefing repository."""

from __future__ import annotations

from datetime import date
from typing import Sequence

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.briefing import Briefing
from app.repositories.base import BaseRepository

logger = get_logger(__name__)


class BriefingRepository(BaseRepository[Briefing]):
    """Repository for Briefing CRUD and lookup operations."""

    model = Briefing

    async def get_latest_by_type(self, briefing_type: str) -> Briefing | None:
        """Fetch the most recent briefing of a specific type.

        Args:
            briefing_type: One of 'morning', 'daily', or 'weekly'.

        Returns:
            The latest Briefing of that type, or None.
        """
        stmt = (
            select(Briefing)
            .where(Briefing.briefing_type == briefing_type)
            .order_by(Briefing.generated_at.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_date_and_type(
        self, briefing_date: date, briefing_type: str
    ) -> Briefing | None:
        """Fetch a briefing for a specific date and type.

        Args:
            briefing_date: Target date.
            briefing_type: Briefing type string.

        Returns:
            Briefing instance or None.
        """
        stmt = select(Briefing).where(
            and_(
                Briefing.briefing_date == briefing_date,
                Briefing.briefing_type == briefing_type,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_type(
        self,
        briefing_type: str,
        limit: int = 10,
    ) -> Sequence[Briefing]:
        """List recent briefings of a given type.

        Args:
            briefing_type: Briefing type to filter by.
            limit: Maximum results.

        Returns:
            List of recent briefings.
        """
        stmt = (
            select(Briefing)
            .where(Briefing.briefing_type == briefing_type)
            .order_by(Briefing.generated_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
