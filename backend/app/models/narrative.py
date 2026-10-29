"""Narrative ORM model."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text, func, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database import Base


class Narrative(Base):
    """A thematic narrative grouping related articles."""

    __tablename__ = "narratives"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    trend_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    momentum: Mapped[str] = mapped_column(String(32), nullable=False, default="stable")
    sentiment: Mapped[str | None] = mapped_column(String(32), nullable=True)
    article_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    first_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    articles: Mapped[list["Article"]] = relationship(
        "Article",
        secondary="article_narratives",
        back_populates="narratives",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Narrative(id={self.id}, title='{self.title[:50]}...', momentum='{self.momentum}')>"


from app.models.article import Article  # noqa: E402
