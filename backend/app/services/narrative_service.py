"""Narrative service encapsulating business logic."""

from __future__ import annotations

from typing import Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.core.logging import get_logger
from app.models.narrative import Narrative
from app.repositories.narrative_repo import NarrativeRepository

logger = get_logger(__name__)


class NarrativeService:
    """Service layer for narrative operations."""

    def __init__(self, session: AsyncSession) -> None:
        from app.repositories.article_repo import ArticleRepository
        self.repo = NarrativeRepository(session)
        self.article_repo = ArticleRepository(session)
        self.session = session

    async def get_narrative(self, narrative_id: UUID) -> Narrative:
        """Fetch a single narrative by ID with related articles.

        Args:
            narrative_id: The narrative's UUID.

        Returns:
            The Narrative instance.

        Raises:
            NotFoundError: If the narrative does not exist.
        """
        return await self.repo.get_by_id(narrative_id)

    async def list_narratives(
        self,
        *,
        trending: bool = False,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[Sequence[Narrative], int]:
        """List narratives with pagination.

        Args:
            trending: If True, sort by trend score.
            page: Page number (1-based).
            limit: Page size.

        Returns:
            Tuple of (narratives, total_count).
        """
        offset = (page - 1) * limit
        return await self.repo.list_paginated(
            trending=trending,
            offset=offset,
            limit=limit,
        )

    async def get_trending_narratives(self, limit: int = 5) -> Sequence[Narrative]:
        """Fetch top trending narratives.

        Args:
            limit: Max results.

        Returns:
            List of trending narratives.
        """
        return await self.repo.get_trending(limit)

    async def detect_and_save_narratives(self) -> int:
        """Query recent articles, run the NarrativeDetectionAgent, and save/update narratives in the database."""
        from datetime import datetime, timedelta
        from app.agents.narrative_agent import NarrativeDetectionAgent
        from app.models.narrative import Narrative
        
        # Get articles from the last 7 days
        since_date = datetime.utcnow() - timedelta(days=7)
        articles, total = await self.article_repo.list_filtered(
            date_from=since_date,
            limit=100
        )
        
        if len(articles) < 3:
            logger.info("not_enough_articles_for_narrative_detection", count=len(articles))
            return 0
            
        # Format article data for the agent
        article_dicts = []
        for art in articles:
            article_dicts.append({
                "id": str(art.id),
                "title": art.title,
                "summary": art.summary or art.content,
                "source": art.source,
            })
            
        agent = NarrativeDetectionAgent()
        output = await agent.process({"articles": article_dicts})
        
        detected_count = 0
        for dn in output.narratives:
            # Check if narrative already exists by title
            narrative = await self.repo.get_by_title(dn.title)
            if not narrative:
                from uuid import uuid4
                narrative = Narrative(
                    id=uuid4(),
                    title=dn.title,
                    description=dn.description,
                    trend_score=dn.trend_score,
                    momentum=dn.momentum,
                    sentiment=dn.sentiment,
                    article_count=0
                )
                self.session.add(narrative)
            else:
                # Update narrative details
                narrative.description = dn.description
                narrative.trend_score = dn.trend_score
                narrative.momentum = dn.momentum
                narrative.sentiment = dn.sentiment
                
            # Associate articles
            for idx in dn.related_article_indices:
                if 0 <= idx < len(articles):
                    art = articles[idx]
                    # Link if not already linked
                    if art not in narrative.articles:
                        narrative.articles.append(art)
            
            narrative.article_count = len(narrative.articles)
            narrative.last_updated = datetime.utcnow()
            detected_count += 1
            
        await self.session.commit()
        logger.info("narrative_detection_service_complete", detected_count=detected_count)
        return detected_count
