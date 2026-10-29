"""FastAPI dependency injection provider for services and connections."""

from __future__ import annotations

from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database import get_db_session
from app.services.article_service import ArticleService
from app.services.briefing_service import BriefingService
from app.services.company_service import CompanyService
from app.services.event_service import EventService
from app.services.market_pulse_service import MarketPulseService
from app.services.narrative_service import NarrativeService
from app.services.rag_service import RAGService


async def get_article_service(
    session: AsyncSession = Depends(get_db_session),
) -> ArticleService:
    """Dependency that yields an ArticleService instance."""
    return ArticleService(session)


async def get_event_service(
    session: AsyncSession = Depends(get_db_session),
) -> EventService:
    """Dependency that yields an EventService instance."""
    return EventService(session)


async def get_narrative_service(
    session: AsyncSession = Depends(get_db_session),
) -> NarrativeService:
    """Dependency that yields a NarrativeService instance."""
    return NarrativeService(session)


async def get_market_pulse_service(
    session: AsyncSession = Depends(get_db_session),
) -> MarketPulseService:
    """Dependency that yields a MarketPulseService instance."""
    return MarketPulseService(session)


async def get_briefing_service(
    session: AsyncSession = Depends(get_db_session),
) -> BriefingService:
    """Dependency that yields a BriefingService instance."""
    return BriefingService(session)


async def get_company_service(
    session: AsyncSession = Depends(get_db_session),
) -> CompanyService:
    """Dependency that yields a CompanyService instance."""
    return CompanyService(session)


async def get_rag_service() -> RAGService:
    """Dependency that yields a RAGService instance (singleton-like)."""
    return RAGService()
