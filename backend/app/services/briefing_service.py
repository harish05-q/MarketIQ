"""Briefing service encapsulating business logic."""

from __future__ import annotations

from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.core.logging import get_logger
from app.models.briefing import Briefing
from app.repositories.briefing_repo import BriefingRepository

logger = get_logger(__name__)


class BriefingService:
    """Service layer for market briefing operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.repo = BriefingRepository(session)
        self.session = session

    async def get_latest_briefing(self, briefing_type: str) -> Briefing | None:
        """Fetch the most recent briefing of a given type.

        Args:
            briefing_type: One of 'morning', 'daily', 'weekly'.

        Returns:
            The latest Briefing or None.
        """
        return await self.repo.get_latest_by_type(briefing_type)

    async def create_briefing(
        self,
        briefing_type: str,
        content: str,
        sections: list[dict] | None = None,
        briefing_date: date | None = None,
    ) -> Briefing:
        """Create and persist a new briefing.

        Args:
            briefing_type: Briefing type string.
            content: Full briefing text.
            sections: Optional structured sections.
            briefing_date: Date of the briefing. Defaults to today.

        Returns:
            The created Briefing.
        """
        briefing = Briefing(
            briefing_type=briefing_type,
            content=content,
            sections=sections or [],
            briefing_date=briefing_date or date.today(),
        )
        return await self.repo.create(briefing)

    async def generate_and_save_briefing(self, briefing_type: str = "daily") -> Briefing:
        """Retrieve recent market data, run the MarketBriefingAgent, and save the briefing."""
        from datetime import datetime, timedelta
        from app.agents.briefing_agent import MarketBriefingAgent
        from app.repositories.article_repo import ArticleRepository
        from app.repositories.event_repo import EventRepository
        from app.repositories.narrative_repo import NarrativeRepository
        
        art_repo = ArticleRepository(self.session)
        evt_repo = EventRepository(self.session)
        nar_repo = NarrativeRepository(self.session)
        
        # Determine time window
        days = 7 if briefing_type == "weekly" else 1
        since_date = datetime.utcnow() - timedelta(days=days)
        
        # Fetch articles
        articles_raw, _ = await art_repo.list_filtered(date_from=since_date, limit=50)
        articles = [{"title": a.title, "source": a.source, "sentiment": a.sentiment, "summary": a.summary or a.content} for a in articles_raw]
        
        # Fetch events
        events_raw = await evt_repo.get_recent_events(limit=20)
        events = [{"event_type": e.event_type, "severity": e.severity, "affected_entities": e.affected_entities or []} for e in events_raw]
        
        # Fetch narratives
        narratives_raw = await nar_repo.get_active_narratives(min_articles=2)
        narratives = [{"title": n.title, "momentum": n.momentum, "trend_score": n.trend_score} for n in narratives_raw]
        
        # Fetch sentiment summary
        avg_sentiment = await art_repo.get_average_sentiment_score()
        sentiment_dist = await art_repo.get_sentiment_distribution()
        sentiment_summary = {
            "average_score": avg_sentiment,
            "distribution": sentiment_dist
        }
        
        agent = MarketBriefingAgent()
        output = await agent.process({
            "briefing_type": briefing_type,
            "articles": articles,
            "events": events,
            "narratives": narratives,
            "sentiment_summary": sentiment_summary,
        })
        
        # Format sections for model saving
        sections_data = [
            {"title": s.title, "content": s.content, "key_points": s.key_points}
            for s in output.sections
        ]
        
        briefing = Briefing(
            briefing_type=briefing_type,
            content=output.content,
            sections=sections_data,
            briefing_date=date.today(),
        )
        self.session.add(briefing)
        await self.session.commit()
        logger.info("briefing_service_generation_complete", briefing_type=briefing_type)
        return briefing
