"""Article API endpoints."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.core.exceptions import NotFoundError
from app.dependencies import get_article_service
from app.schemas.article import ArticleListResponse, ArticleResponse, PaginationMeta, ArticleDetail, ArticleSummary
from app.services.article_service import ArticleService

router = APIRouter(prefix="/articles", tags=["articles"])


@router.get("", response_model=ArticleListResponse)
async def list_articles(
    source: str | None = Query(None, description="Filter by publisher source"),
    sentiment: str | None = Query(None, description="Filter by sentiment (bullish, bearish, etc.)"),
    sector: str | None = Query(None, description="Filter by sector name"),
    date_from: datetime | None = Query(None, description="Start date filter"),
    date_to: datetime | None = Query(None, description="End date filter"),
    search: str | None = Query(None, description="Keyword search in title/content"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    service: ArticleService = Depends(get_article_service),
) -> ArticleListResponse:
    """List financial articles with filtering and pagination."""
    articles, total = await service.list_articles(
        source=source,
        sentiment=sentiment,
        sector=sector,
        date_from=date_from,
        date_to=date_to,
        search=search,
        page=page,
        limit=limit,
    )

    summaries = [ArticleSummary.model_validate(art) for art in articles]

    return ArticleListResponse(
        success=True,
        data=summaries,
        meta=PaginationMeta(page=page, limit=limit, total=total),
    )


@router.get("/{article_id}", response_model=ArticleResponse)
async def get_article(
    article_id: UUID,
    service: ArticleService = Depends(get_article_service),
) -> ArticleResponse:
    """Retrieve full article detail including extracted entities and events."""
    try:
        article = await service.get_article(article_id)
        return ArticleResponse(
            success=True,
            data=ArticleDetail.model_validate(article),
        )
    except NotFoundError as e:
        raise e
