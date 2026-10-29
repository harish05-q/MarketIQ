"""Narrative API endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from app.core.exceptions import NotFoundError
from app.dependencies import get_narrative_service
from app.schemas.narrative import NarrativeDetail, NarrativeListResponse, NarrativeResponse, PaginationMeta
from app.services.narrative_service import NarrativeService

router = APIRouter(prefix="/narratives", tags=["narratives"])


class NarrativeDetailResponse(BaseModel):
    """Response wrapper for narrative details."""

    success: bool = True
    data: NarrativeDetail


@router.get("", response_model=NarrativeListResponse)
async def list_narratives(
    trending: bool = Query(False, description="Sort by trend score if True"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    service: NarrativeService = Depends(get_narrative_service),
) -> NarrativeListResponse:
    """List narratives with pagination, optionally sorted by trend score."""
    narratives, total = await service.list_narratives(
        trending=trending,
        page=page,
        limit=limit,
    )

    data = [NarrativeResponse.model_validate(nar) for nar in narratives]

    return NarrativeListResponse(
        success=True,
        data=data,
        meta=PaginationMeta(page=page, limit=limit, total=total),
    )


@router.get("/{narrative_id}", response_model=NarrativeDetailResponse)
async def get_narrative(
    narrative_id: UUID,
    service: NarrativeService = Depends(get_narrative_service),
) -> NarrativeDetailResponse:
    """Retrieve narrative details with associated articles."""
    try:
        narrative = await service.get_narrative(narrative_id)
        return NarrativeDetailResponse(
            success=True,
            data=NarrativeDetail.model_validate(narrative),
        )
    except NotFoundError as e:
        raise e
