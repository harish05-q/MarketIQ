"""Ingest API endpoints."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, BackgroundTasks
from pydantic import BaseModel

from app.agents.ingestion_agent import IngestionAgent
from app.dependencies import get_article_service
from app.services.article_service import ArticleService

router = APIRouter(prefix="/ingest", tags=["ingest"])


class IngestResponse(BaseModel):
    """Response wrapper for ingestion triggers."""

    success: bool = True
    data: dict[str, Any]


async def run_ingestion_task(article_service: ArticleService) -> dict[str, Any]:
    """Orchestrate the ingestion process using the IngestionAgent."""
    # Retrieve URLs from articles published in the last 7 days to deduplicate
    since_date = datetime.utcnow() - timedelta(days=7)
    recent_articles = await article_service.get_recent_articles(since=since_date, limit=1000)
    seen_urls = {art.source_url for art in recent_articles}

    async def process_callback(raw_article: dict[str, Any]):
        await article_service.process_and_save_raw_article(raw_article)

    agent = IngestionAgent(seen_urls=seen_urls, process_callback=process_callback)
    stats = await agent.process()

    # Trigger post-ingest intelligence clustering and briefings if new articles were fetched
    if stats.get("total_new", 0) > 0:
        try:
            from app.services.narrative_service import NarrativeService
            from app.services.briefing_service import BriefingService
            
            session = article_service.session
            
            # 1. Detect and cluster narratives
            narrative_service = NarrativeService(session)
            detected_count = await narrative_service.detect_and_save_narratives()
            stats["detected_narratives_count"] = detected_count
            
            # 2. Generate briefings
            briefing_service = BriefingService(session)
            await briefing_service.generate_and_save_briefing(briefing_type="daily")
            await briefing_service.generate_and_save_briefing(briefing_type="morning")
            stats["briefings_generated"] = ["daily", "morning"]
        except Exception as exc:
            from app.core.logging import get_logger
            logger = get_logger(__name__)
            logger.error("post_ingestion_agents_failed", error=str(exc))
            
    return stats


@router.post("", response_model=IngestResponse)
async def trigger_ingest(
    background_tasks: BackgroundTasks,
    service: ArticleService = Depends(get_article_service),
) -> IngestResponse:
    """Trigger the news ingestion process.

    This runs asynchronously in the background. It fetches new articles,
    deduplicates them, and publishes them to the Kafka queue.
    """
    # Trigger ingestion
    stats = await run_ingestion_task(service)
    
    return IngestResponse(
        success=True,
        data={
            "message": "Ingestion cycle executed.",
            "stats": stats
        },
    )
