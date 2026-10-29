"""Narrative Pydantic schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.article import ArticleSummary


class NarrativeResponse(BaseModel):
    """Compact narrative representation for list endpoints."""

    id: UUID
    title: str
    description: str | None = None
    trend_score: float
    momentum: str
    sentiment: str | None = None
    article_count: int
    first_seen: datetime
    last_updated: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NarrativeDetail(BaseModel):
    """Full narrative representation with related articles."""

    id: UUID
    title: str
    description: str | None = None
    trend_score: float
    momentum: str
    sentiment: str | None = None
    article_count: int
    first_seen: datetime
    last_updated: datetime
    articles: list[ArticleSummary] = Field(default_factory=list)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginationMeta(BaseModel):
    """Pagination metadata."""

    page: int
    limit: int
    total: int


class NarrativeListResponse(BaseModel):
    """Paginated narrative list API response."""

    success: bool = True
    data: list[NarrativeResponse]
    meta: PaginationMeta
