"""Event repository."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Sequence
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.logging import get_logger
from app.models.article import Article
from app.models.event import Event
from app.repositories.base import BaseRepository

logger = get_logger(__name__)


class EventRepository(BaseRepository[Event]):
    """Repository for Event CRUD and filtered queries."""

    model = Event

    async def list_filtered(
        self,
        *,
        event_type: str | None = None,
        severity: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[Sequence[dict[str, Any]], int]:
        """Return a filtered and paginated list of events with article context.

        Args:
            event_type: Filter by event type.
            severity: Filter by severity level.
            date_from: Minimum detection date.
            date_to: Maximum detection date.
            offset: Pagination offset.
            limit: Page size.

        Returns:
            Tuple of (events_with_article_info, total_count).
        """
        conditions: list[Any] = []
        if event_type:
            conditions.append(Event.event_type == event_type)
        if severity:
            conditions.append(Event.severity == severity)
        if date_from:
            conditions.append(Event.detected_at >= date_from)
        if date_to:
            conditions.append(Event.detected_at <= date_to)

        # Count
        count_stmt = select(func.count()).select_from(Event)
        if conditions:
            count_stmt = count_stmt.where(and_(*conditions))
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar_one()

        # Data with article join
        data_stmt = (
            select(
                Event,
                Article.title.label("article_title"),
                Article.source.label("article_source"),
            )
            .join(Article, Event.article_id == Article.id)
        )
        if conditions:
            data_stmt = data_stmt.where(and_(*conditions))
        data_stmt = data_stmt.order_by(Event.detected_at.desc()).offset(offset).limit(limit)

        result = await self.session.execute(data_stmt)
        rows = result.all()

        events_data = []
        for row in rows:
            event = row[0]
            event_dict = {
                "id": event.id,
                "article_id": event.article_id,
                "event_type": event.event_type,
                "severity": event.severity,
                "confidence": event.confidence,
                "affected_entities": event.affected_entities or [],
                "affected_sectors": event.affected_sectors or [],
                "detected_at": event.detected_at,
                "created_at": event.created_at,
                "article_title": row[1],
                "article_source": row[2],
            }
            events_data.append(event_dict)

        return events_data, total

    async def get_recent_events(self, limit: int = 10) -> Sequence[Event]:
        """Fetch the most recent events.

        Args:
            limit: Maximum events to return.

        Returns:
            List of recent events.
        """
        stmt = select(Event).order_by(Event.detected_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_events_by_article(self, article_id: UUID) -> Sequence[Event]:
        """Fetch all events linked to a specific article.

        Args:
            article_id: The article's UUID.

        Returns:
            List of events for that article.
        """
        stmt = select(Event).where(Event.article_id == article_id).order_by(Event.detected_at.desc())
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_events_since(self, since: datetime, limit: int = 100) -> Sequence[Event]:
        """Fetch events detected after a given timestamp.

        Args:
            since: Cutoff datetime.
            limit: Maximum results.

        Returns:
            List of events.
        """
        stmt = (
            select(Event)
            .where(Event.detected_at >= since)
            .order_by(Event.detected_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
