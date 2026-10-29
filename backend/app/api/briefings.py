"""Briefing API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.dependencies import get_briefing_service
from app.schemas.briefing import BriefingDetailResponse, BriefingResponse
from app.services.briefing_service import BriefingService

router = APIRouter(prefix="/briefings", tags=["briefings"])


@router.get("/latest", response_model=BriefingDetailResponse)
async def get_latest_briefing(
    briefing_type: str = Query("daily", description="Type of briefing: 'morning', 'daily', or 'weekly'"),
    service: BriefingService = Depends(get_briefing_service),
) -> BriefingDetailResponse:
    """Retrieve the latest generated market briefing by type."""
    briefing = await service.get_latest_briefing(briefing_type)
    
    if briefing is None:
        return BriefingDetailResponse(success=True, data=None)

    return BriefingDetailResponse(
        success=True,
        data=BriefingResponse.model_validate(briefing),
    )
