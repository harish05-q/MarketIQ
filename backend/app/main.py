"""Main FastAPI application entrypoint."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.core.exceptions import MarketIQError
from app.core.logging import get_logger
from app.infrastructure.database import init_db, close_db
from app.infrastructure.kafka_client import ensure_topics_exist, close_kafka
from app.infrastructure.qdrant_client import ensure_collection_exists, close_qdrant
from app.api.router import api_router

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application startup and shutdown lifecycle events."""
    logger.info("application_startup_initiated")
    
    # Setup database connection and initialize tables (if in development)
    try:
        settings = get_settings()
        if settings.ENVIRONMENT == "development":
            logger.info("development_environment_detected_initializing_db_tables")
            await init_db()
    except Exception as exc:
        logger.error("database_startup_initialization_failed", error=str(exc))
        # Keep running but log failure, or raise. Let's keep going for resiliency.

    # Ensure Kafka topics exist
    try:
        await ensure_topics_exist()
    except Exception as exc:
        logger.error("kafka_startup_topics_check_failed", error=str(exc))

    # Ensure Qdrant collection exists
    try:
        await ensure_collection_exists()
    except Exception as exc:
        logger.error("qdrant_startup_collection_check_failed", error=str(exc))

    logger.info("application_startup_completed")
    
    yield
    
    logger.info("application_shutdown_initiated")
    
    # Close resources
    await close_db()
    close_qdrant()
    close_kafka()
    
    logger.info("application_shutdown_completed")


settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(MarketIQError)
async def market_iq_error_handler(request: Request, exc: MarketIQError) -> JSONResponse:
    """Format custom MarketIQ errors into a unified API error response structure."""
    logger.error(
        "api_error_raised",
        path=request.url.path,
        code=exc.code,
        message=exc.message,
        status_code=exc.status_code,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
            }
        }
    )


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    """API health status endpoint."""
    return {"status": "healthy", "service": settings.APP_NAME}


# Include root API router
app.include_router(api_router, prefix=settings.API_PREFIX)
