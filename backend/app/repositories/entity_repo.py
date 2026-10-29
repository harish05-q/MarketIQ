"""Entity repository."""

from __future__ import annotations

from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.entity import Entity
from app.repositories.base import BaseRepository

logger = get_logger(__name__)


class EntityRepository(BaseRepository[Entity]):
    """Repository for Entity CRUD and lookups."""

    model = Entity

    async def get_by_name_and_type(self, name: str, entity_type: str) -> Entity | None:
        """Find an entity by name and type.

        Args:
            name: Entity name (case-insensitive match).
            entity_type: Entity type string.

        Returns:
            Entity instance or None.
        """
        stmt = select(Entity).where(
            func.lower(Entity.name) == name.lower(),
            Entity.type == entity_type,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_or_create(self, name: str, entity_type: str, confidence: float = 1.0) -> Entity:
        """Find an existing entity or create a new one.

        Args:
            name: Entity name.
            entity_type: Entity type.
            confidence: Confidence score for entity extraction.

        Returns:
            The existing or newly created Entity.
        """
        existing = await self.get_by_name_and_type(name, entity_type)
        if existing is not None:
            return existing

        entity = Entity(name=name, type=entity_type, confidence=confidence)
        return await self.create(entity)

    async def search_by_name(self, query: str, limit: int = 20) -> Sequence[Entity]:
        """Search entities by name prefix.

        Args:
            query: Search string.
            limit: Maximum results.

        Returns:
            Matching entities.
        """
        stmt = (
            select(Entity)
            .where(Entity.name.ilike(f"%{query}%"))
            .order_by(Entity.name)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_type(self, entity_type: str, limit: int = 50) -> Sequence[Entity]:
        """Fetch entities of a specific type.

        Args:
            entity_type: Entity type to filter by.
            limit: Maximum results.

        Returns:
            List of entities of the given type.
        """
        stmt = (
            select(Entity)
            .where(Entity.type == entity_type)
            .order_by(Entity.name)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
