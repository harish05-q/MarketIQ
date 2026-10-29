"""Repository layer for data access."""

from app.repositories.article_repo import ArticleRepository
from app.repositories.briefing_repo import BriefingRepository
from app.repositories.entity_repo import EntityRepository
from app.repositories.event_repo import EventRepository
from app.repositories.narrative_repo import NarrativeRepository

__all__ = [
    "ArticleRepository",
    "BriefingRepository",
    "EntityRepository",
    "EventRepository",
    "NarrativeRepository",
]
