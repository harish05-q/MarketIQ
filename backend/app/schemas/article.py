"""Article Pydantic schemas for request validation and response serialization."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from app.schemas.entity import EntityResponse
from app.schemas.event import EventResponse


# ── Base / Shared ────────────────────────────────────────────────────────────

class ArticleBase(BaseModel):
    """Shared article fields."""

    title: str = Field(..., max_length=1024, description="Article headline")
    content: str = Field(..., min_length=1, description="Full article text")
    source: str = Field(..., max_length=128, description="Source name")
    source_url: str = Field(..., max_length=2048, description="Original article URL")
    published_at: datetime | None = Field(None, description="Publication timestamp")
    metadata_: dict[str, Any] | None = Field(None, alias="metadata", description="Extra metadata")

    model_config = ConfigDict(populate_by_name=True)


# ── Create / Update ─────────────────────────────────────────────────────────

class ArticleCreate(ArticleBase):
    """Schema for creating a new article."""

    pass


class ArticleUpdate(BaseModel):
    """Schema for partially updating an article."""

    summary: str | None = None
    sentiment: str | None = None
    sentiment_score: float | None = Field(None, ge=-1.0, le=1.0)
    impact_score: float | None = Field(None, ge=0.0, le=100.0)
    embedding_id: str | None = None
    metadata_: dict[str, Any] | None = Field(None, alias="metadata")

    model_config = ConfigDict(populate_by_name=True)


# ── Response ─────────────────────────────────────────────────────────────────

class ArticleSummary(BaseModel):
    """Compact article representation for list endpoints."""

    id: UUID
    title: str
    source: str
    source_url: str
    summary: str | None = None
    published_at: datetime | None = None
    sentiment: str | None = None
    sentiment_score: float | None = None
    impact_score: float | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ArticleDetail(BaseModel):
    """Full article representation with relationships."""

    id: UUID
    title: str
    content: str
    summary: str | None = None
    source: str
    source_url: str
    published_at: datetime | None = None
    sentiment: str | None = None
    sentiment_score: float | None = None
    impact_score: float | None = None
    embedding_id: str | None = None
    metadata_: dict[str, Any] | None = Field(None, alias="metadata")
    entities: list[EntityResponse] = Field(default_factory=list)
    events: list[EventResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# ── Paginated Response Wrapper ──────────────────────────────────────────────

class PaginationMeta(BaseModel):
    """Pagination metadata."""

    page: int
    limit: int
    total: int


class ArticleResponse(BaseModel):
    """Standard single-article API response."""

    success: bool = True
    data: ArticleDetail


class ArticleListResponse(BaseModel):
    """Paginated article list API response."""

    success: bool = True
    data: list[ArticleSummary]
    meta: PaginationMeta
