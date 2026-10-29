"""Event Pydantic schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class EventResponse(BaseModel):
    """Event response representation."""

    id: UUID
    article_id: UUID
    event_type: str
    severity: str
    confidence: float
    affected_entities: list[Any] = Field(default_factory=list)
    affected_sectors: list[Any] = Field(default_factory=list)
    detected_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EventWithArticle(EventResponse):
    """Event response with article title for list views."""

    article_title: str | None = None
    article_source: str | None = None


class PaginationMeta(BaseModel):
    """Pagination metadata."""

    page: int
    limit: int
    total: int


class EventListResponse(BaseModel):
    """Paginated event list API response."""

    success: bool = True
    data: list[EventWithArticle]
    meta: PaginationMeta
