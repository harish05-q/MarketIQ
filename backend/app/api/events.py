"""Event API endpoints."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query

from app.dependencies import get_event_service
from app.schemas.event import EventListResponse, EventWithArticle, PaginationMeta
from app.services.event_service import EventService

router = APIRouter(prefix="/events", tags=["events"])


@router.get("", response_model=EventListResponse)
async def list_events(
    event_type: str | None = Query(None, description="Filter by event type"),
    severity: str | None = Query(None, description="Filter by severity (critical, high, info, etc.)"),
    date_from: datetime | None = Query(None, description="Filter by start date"),
    date_to: datetime | None = Query(None, description="Filter by end date"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    service: EventService = Depends(get_event_service),
) -> EventListResponse:
    """List detected market events with pagination and filtering."""
    events, total = await service.list_events(
        event_type=event_type,
        severity=severity,
        date_from=date_from,
        date_to=date_to,
        page=page,
        limit=limit,
    )

    data = [EventWithArticle.model_validate(evt) for evt in events]

    return EventListResponse(
        success=True,
        data=data,
        meta=PaginationMeta(page=page, limit=limit, total=total),
    )
