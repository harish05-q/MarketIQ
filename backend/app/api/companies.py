"""Company API endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.dependencies import get_company_service
from app.services.company_service import CompanyService

router = APIRouter(prefix="/companies", tags=["companies"])


class CompanyResponse(BaseModel):
    """Response wrapper for company profile details."""

    success: bool = True
    data: dict[str, Any]


@router.get("/{ticker}", response_model=CompanyResponse)
async def get_company_profile(
    ticker: str,
    service: CompanyService = Depends(get_company_service),
) -> CompanyResponse:
    """Retrieve intelligence profile for a specific company by ticker symbol."""
    profile = await service.get_company_profile(ticker)
    return CompanyResponse(
        success=True,
        data=profile,
    )
