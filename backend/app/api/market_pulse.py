"""Market Pulse API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.dependencies import get_market_pulse_service
from app.schemas.market_pulse import MarketPulseResponse
from app.services.market_pulse_service import MarketPulseService

router = APIRouter(prefix="/market-pulse", tags=["market-pulse"])


@router.get("", response_model=MarketPulseResponse)
async def get_market_pulse(
    service: MarketPulseService = Depends(get_market_pulse_service),
) -> MarketPulseResponse:
    """Retrieve the dashboard overview metrics (Market Pulse)."""
    data = await service.get_market_pulse()
    return MarketPulseResponse(
        success=True,
        data=data,
    )
