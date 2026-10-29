"""Root API router aggregating all endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.articles import router as articles_router
from app.api.briefings import router as briefings_router
from app.api.chat import router as chat_router
from app.api.companies import router as companies_router
from app.api.events import router as events_router
from app.api.ingest import router as ingest_router
from app.api.market_pulse import router as market_pulse_router
from app.api.narratives import router as narratives_router

api_router = APIRouter()

# Include sub-routers
api_router.include_router(articles_router)
api_router.include_router(events_router)
api_router.include_router(narratives_router)
api_router.include_router(market_pulse_router)
api_router.include_router(briefings_router)
api_router.include_router(chat_router)
api_router.include_router(ingest_router)
api_router.include_router(companies_router)
