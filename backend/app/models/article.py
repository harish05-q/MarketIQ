"""Article ORM model and association tables."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    String,
    Table,
    Text,
    func,
    JSON,
    UUID,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database import Base


class ArticleEntity(Base):
    """Association table linking articles to extracted entities."""

    __tablename__ = "article_entities"

    article_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("articles.id", ondelete="CASCADE"),
        primary_key=True,
    )
    entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("entities.id", ondelete="CASCADE"),
        primary_key=True,
    )


class ArticleNarrative(Base):
    """Association table linking articles to detected narratives."""

    __tablename__ = "article_narratives"

    article_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("articles.id", ondelete="CASCADE"),
        primary_key=True,
    )
    narrative_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("narratives.id", ondelete="CASCADE"),
        primary_key=True,
    )


class Article(Base):
    """Represents an ingested and processed news article."""

    __tablename__ = "articles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(1024), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    source_url: Mapped[str] = mapped_column(String(2048), nullable=False, unique=True)
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    sentiment: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    sentiment_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    impact_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    embedding_id: Mapped[str | None] = mapped_column(String(256), nullable=True)
    metadata_: Mapped[dict | None] = mapped_column(
        "metadata", JSON, nullable=True, default=dict
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    entities: Mapped[list["Entity"]] = relationship(
        "Entity",
        secondary="article_entities",
        back_populates="articles",
        lazy="selectin",
    )
    events: Mapped[list["Event"]] = relationship(
        "Event", back_populates="article", lazy="selectin", cascade="all, delete-orphan"
    )
    narratives: Mapped[list["Narrative"]] = relationship(
        "Narrative",
        secondary="article_narratives",
        back_populates="articles",
        lazy="selectin",
    )

    # Indices for common query patterns
    __table_args__ = (
        Index("ix_articles_source_published", "source", "published_at"),
        Index("ix_articles_sentiment_score", "sentiment", "sentiment_score"),
        Index("ix_articles_impact_score", "impact_score"),
    )

    def __repr__(self) -> str:
        return f"<Article(id={self.id}, title='{self.title[:50]}...', source='{self.source}')>"


# Avoid circular import – Entity is imported via string reference above
from app.models.entity import Entity  # noqa: E402
from app.models.event import Event  # noqa: E402
from app.models.narrative import Narrative  # noqa: E402
