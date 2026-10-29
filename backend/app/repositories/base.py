"""Generic base repository with common CRUD operations."""

from __future__ import annotations

from typing import Any, Generic, Sequence, Type, TypeVar
from uuid import UUID

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DatabaseError, NotFoundError
from app.core.logging import get_logger
from app.infrastructure.database import Base

ModelT = TypeVar("ModelT", bound=Base)

logger = get_logger(__name__)


class BaseRepository(Generic[ModelT]):
    """Generic async repository providing CRUD operations for SQLAlchemy models.

    Subclasses should set ``model`` to the ORM class they manage.
    """

    model: Type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, id: UUID) -> ModelT:
        """Fetch a single record by primary key.

        Args:
            id: Primary key UUID.

        Returns:
            The matching model instance.

        Raises:
            NotFoundError: If no record with the given id exists.
        """
        try:
            result = await self.session.get(self.model, id)
            if result is None:
                raise NotFoundError(self.model.__tablename__, str(id))
            return result
        except NotFoundError:
            raise
        except Exception as exc:
            logger.error("db_get_by_id_error", model=self.model.__tablename__, id=str(id), error=str(exc))
            raise DatabaseError(f"Failed to fetch {self.model.__tablename__}: {exc}") from exc

    async def get_all(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
        order_by: Any | None = None,
    ) -> Sequence[ModelT]:
        """Fetch a paginated list of records.

        Args:
            offset: Number of records to skip.
            limit: Maximum records to return.
            order_by: Optional SQLAlchemy column expression for ordering.

        Returns:
            Sequence of model instances.
        """
        try:
            stmt = select(self.model)
            if order_by is not None:
                stmt = stmt.order_by(order_by)
            stmt = stmt.offset(offset).limit(limit)
            result = await self.session.execute(stmt)
            return result.scalars().all()
        except Exception as exc:
            logger.error("db_get_all_error", model=self.model.__tablename__, error=str(exc))
            raise DatabaseError(f"Failed to fetch {self.model.__tablename__} list: {exc}") from exc

    async def count(self) -> int:
        """Return the total number of records.

        Returns:
            Integer count.
        """
        try:
            stmt = select(func.count()).select_from(self.model)
            result = await self.session.execute(stmt)
            return result.scalar_one()
        except Exception as exc:
            logger.error("db_count_error", model=self.model.__tablename__, error=str(exc))
            raise DatabaseError(f"Failed to count {self.model.__tablename__}: {exc}") from exc

    async def create(self, entity: ModelT) -> ModelT:
        """Persist a new model instance.

        Args:
            entity: The ORM model instance to insert.

        Returns:
            The persisted model instance with generated fields populated.
        """
        try:
            self.session.add(entity)
            await self.session.flush()
            await self.session.refresh(entity)
            return entity
        except Exception as exc:
            logger.error("db_create_error", model=self.model.__tablename__, error=str(exc))
            raise DatabaseError(f"Failed to create {self.model.__tablename__}: {exc}") from exc

    async def create_many(self, entities: list[ModelT]) -> list[ModelT]:
        """Bulk insert multiple model instances.

        Args:
            entities: List of ORM model instances.

        Returns:
            The persisted instances.
        """
        try:
            self.session.add_all(entities)
            await self.session.flush()
            for entity in entities:
                await self.session.refresh(entity)
            return entities
        except Exception as exc:
            logger.error("db_create_many_error", model=self.model.__tablename__, error=str(exc))
            raise DatabaseError(f"Failed to bulk create {self.model.__tablename__}: {exc}") from exc

    async def update_by_id(self, id: UUID, values: dict[str, Any]) -> ModelT:
        """Update specific fields of a record by primary key.

        Args:
            id: Primary key UUID.
            values: Dictionary of column-name → new-value.

        Returns:
            The updated model instance.

        Raises:
            NotFoundError: If no record with the given id exists.
        """
        try:
            entity = await self.get_by_id(id)
            for key, value in values.items():
                setattr(entity, key, value)
            await self.session.flush()
            await self.session.refresh(entity)
            return entity
        except NotFoundError:
            raise
        except Exception as exc:
            logger.error("db_update_error", model=self.model.__tablename__, id=str(id), error=str(exc))
            raise DatabaseError(f"Failed to update {self.model.__tablename__}: {exc}") from exc

    async def delete_by_id(self, id: UUID) -> None:
        """Delete a record by primary key.

        Args:
            id: Primary key UUID.

        Raises:
            NotFoundError: If no record with the given id exists.
        """
        try:
            entity = await self.get_by_id(id)
            await self.session.delete(entity)
            await self.session.flush()
        except NotFoundError:
            raise
        except Exception as exc:
            logger.error("db_delete_error", model=self.model.__tablename__, id=str(id), error=str(exc))
            raise DatabaseError(f"Failed to delete {self.model.__tablename__}: {exc}") from exc

    async def exists(self, id: UUID) -> bool:
        """Check whether a record exists by primary key.

        Args:
            id: Primary key UUID.

        Returns:
            True if the record exists.
        """
        try:
            stmt = select(func.count()).select_from(self.model).where(self.model.id == id)
            result = await self.session.execute(stmt)
            return result.scalar_one() > 0
        except Exception as exc:
            logger.error("db_exists_error", model=self.model.__tablename__, id=str(id), error=str(exc))
            raise DatabaseError(f"Failed to check existence in {self.model.__tablename__}: {exc}") from exc
