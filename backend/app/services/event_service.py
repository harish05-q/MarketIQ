"""Event service encapsulating business logic."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.event import Event
from app.repositories.event_repo import EventRepository

logger = get_logger(__name__)


class EventService:
    """Service layer for market event operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.repo = EventRepository(session)
        self.session = session

    async def get_event(self, event_id: UUID) -> Event:
        """Fetch a single event by ID.

        Args:
            event_id: The event's UUID.

        Returns:
            The Event instance.

        Raises:
            NotFoundError: If the event does not exist.
        """
        return await self.repo.get_by_id(event_id)

    async def list_events(
        self,
        *,
        event_type: str | None = None,
        severity: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[Sequence[dict[str, Any]], int]:
        """List events with optional filters and pagination.

        Args:
            event_type: Filter by event type.
            severity: Filter by severity.
            date_from: Minimum detection date.
            date_to: Maximum detection date.
            page: Page number (1-based).
            limit: Page size.

        Returns:
            Tuple of (events_with_context, total_count).
        """
        offset = (page - 1) * limit
        return await self.repo.list_filtered(
            event_type=event_type,
            severity=severity,
            date_from=date_from,
            date_to=date_to,
            offset=offset,
            limit=limit,
        )

    async def create_event(
        self,
        article_id: UUID,
        event_type: str,
        severity: str,
        confidence: float,
        affected_entities: list[Any] | None = None,
        affected_sectors: list[Any] | None = None,
    ) -> Event:
        """Create a new market event.

        Args:
            article_id: ID of the source article.
            event_type: Type of market event.
            severity: Severity level.
            confidence: Detection confidence.
            affected_entities: JSON-serializable list of affected entities.
            affected_sectors: JSON-serializable list of affected sectors.

        Returns:
            The created Event.
        """
        event = Event(
            article_id=article_id,
            event_type=event_type,
            severity=severity,
            confidence=confidence,
            affected_entities=affected_entities or [],
            affected_sectors=affected_sectors or [],
        )
        return await self.repo.create(event)

    async def get_recent_events(self, limit: int = 10) -> Sequence[Event]:
        """Fetch the most recent events.

        Args:
            limit: Max results.

        Returns:
            List of recent events.
        """
        return await self.repo.get_recent_events(limit)
