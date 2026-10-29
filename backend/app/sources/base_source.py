"""Base source adapter defining the interface for all RSS feed sources."""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

import feedparser
from pydantic import BaseModel, Field

from app.core.exceptions import ExternalServiceError
from app.core.logging import get_logger

logger = get_logger(__name__)


class RawArticle(BaseModel):
    """Normalized representation of an article fetched from an RSS feed."""

    title: str
    content: str
    source: str
    source_url: str
    published_at: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class BaseSource(ABC):
    """Abstract base class for RSS feed source adapters.

    Subclasses must implement ``source_name``, ``feed_urls``, and
    ``parse_entry`` to handle source-specific RSS field mappings.
    """

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Canonical name of this source (e.g., 'reuters')."""
        ...

    @property
    @abstractmethod
    def feed_urls(self) -> list[str]:
        """List of RSS feed URLs to fetch from this source."""
        ...

    def parse_entry(self, entry: Any) -> RawArticle | None:
        """Parse a single feedparser entry into a RawArticle.

        Override in subclasses for source-specific field mapping.
        Returns None if the entry cannot be parsed.

        Args:
            entry: A feedparser entry object.

        Returns:
            Normalized RawArticle or None.
        """
        try:
            title = getattr(entry, "title", None)
            link = getattr(entry, "link", None)

            if not title or not link:
                return None

            # Extract content – try multiple common RSS content fields
            content = ""
            if hasattr(entry, "content") and entry.content:
                content = entry.content[0].get("value", "")
            elif hasattr(entry, "summary"):
                content = entry.summary or ""
            elif hasattr(entry, "description"):
                content = entry.description or ""

            # Clean HTML tags from content (basic strip)
            content = self._strip_html(content)

            if not content:
                content = title  # Fallback to title if no content

            # Parse published date
            published_at = None
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                try:
                    published_at = datetime(*entry.published_parsed[:6])
                except (TypeError, ValueError):
                    pass
            elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                try:
                    published_at = datetime(*entry.updated_parsed[:6])
                except (TypeError, ValueError):
                    pass

            # Extract tags/categories
            tags = []
            if hasattr(entry, "tags"):
                tags = [tag.get("term", "") for tag in entry.tags if tag.get("term")]

            return RawArticle(
                title=title.strip(),
                content=content.strip(),
                source=self.source_name,
                source_url=link.strip(),
                published_at=published_at,
                metadata={
                    "tags": tags,
                    "author": getattr(entry, "author", None),
                },
            )
        except Exception as exc:
            logger.warning(
                "parse_entry_failed",
                source=self.source_name,
                error=str(exc),
            )
            return None

    async def fetch_articles(self, max_articles: int = 50) -> list[RawArticle]:
        """Fetch and parse articles from all configured feed URLs.

        Runs feedparser in a thread executor since it performs blocking I/O.

        Args:
            max_articles: Maximum articles to return per source.

        Returns:
            List of normalized RawArticle instances.

        Raises:
            ExternalServiceError: If all feeds fail to fetch.
        """
        articles: list[RawArticle] = []
        errors: list[str] = []

        for feed_url in self.feed_urls:
            try:
                loop = asyncio.get_event_loop()
                feed = await loop.run_in_executor(None, feedparser.parse, feed_url)

                if feed.bozo and not feed.entries:
                    errors.append(f"Feed parse error for {feed_url}: {feed.bozo_exception}")
                    logger.warning(
                        "feed_parse_error",
                        source=self.source_name,
                        url=feed_url,
                        error=str(feed.bozo_exception),
                    )
                    continue

                for entry in feed.entries:
                    if len(articles) >= max_articles:
                        break

                    raw_article = self.parse_entry(entry)
                    if raw_article is not None:
                        articles.append(raw_article)

                logger.info(
                    "feed_fetched",
                    source=self.source_name,
                    url=feed_url,
                    articles_count=len(feed.entries),
                )

            except Exception as exc:
                errors.append(f"Failed to fetch {feed_url}: {exc}")
                logger.error(
                    "feed_fetch_error",
                    source=self.source_name,
                    url=feed_url,
                    error=str(exc),
                )

        if not articles and errors:
            raise ExternalServiceError(
                self.source_name,
                f"All feeds failed: {'; '.join(errors)}",
            )

        logger.info(
            "source_fetch_complete",
            source=self.source_name,
            total_articles=len(articles),
        )
        return articles[:max_articles]

    @staticmethod
    def _strip_html(text: str) -> str:
        """Remove HTML tags from text using a simple regex-free approach.

        Args:
            text: Raw HTML string.

        Returns:
            Plain text with HTML tags removed.
        """
        import re
        clean = re.sub(r"<[^>]+>", " ", text)
        clean = re.sub(r"\s+", " ", clean)
        return clean.strip()
