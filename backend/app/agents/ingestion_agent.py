"""Ingestion agent: fetches RSS feeds, deduplicates, normalizes, and pushes to Kafka."""

from __future__ import annotations

import json
from typing import Any

from app.agents.base_agent import BaseAgent
from app.config import get_settings
from app.core.constants import KafkaTopic
from app.core.exceptions import IngestionError
from app.core.logging import get_logger
from app.infrastructure.kafka_client import produce_message
from app.sources.base_source import BaseSource, RawArticle
from app.sources.investing_com import InvestingComSource
from app.sources.marketwatch import MarketWatchSource
from app.sources.reuters import ReutersSource
from app.sources.yahoo_finance import YahooFinanceSource

logger = get_logger(__name__)


class IngestionAgent(BaseAgent):
    """Fetches articles from all configured RSS sources, deduplicates,
    normalizes, and publishes to the raw-articles Kafka topic.

    This agent does not use the LLM – it orchestrates data collection
    and deduplication using feedparser and URL-based checks.
    """

    def __init__(self, seen_urls: set[str] | None = None, process_callback: Any = None) -> None:
        # Skip LLM initialization for this agent – it doesn't need one
        self._logger = get_logger(self.__class__.__name__, agent=self.agent_name)
        self.settings = get_settings()
        self._seen_urls: set[str] = seen_urls or set()
        self.process_callback = process_callback

        # Register all source adapters
        self._sources: list[BaseSource] = [
            ReutersSource(),
            YahooFinanceSource(),
            MarketWatchSource(),
            InvestingComSource(),
        ]

    @property
    def agent_name(self) -> str:
        return "IngestionAgent"

    @property
    def system_prompt(self) -> str:
        return ""  # Not used by this agent

    async def process(self, data: Any = None) -> dict[str, Any]:
        """Run the full ingestion cycle across all sources.

        Args:
            data: Unused, present for interface compliance.

        Returns:
            Summary dict with ingestion statistics.

        Raises:
            IngestionError: If ingestion completely fails.
        """
        self._logger.info("ingestion_started")

        total_fetched = 0
        total_new = 0
        total_duplicates = 0
        source_stats: list[dict[str, Any]] = []
        errors: list[str] = []

        for source in self._sources:
            try:
                articles = await source.fetch_articles(
                    max_articles=self.settings.INGESTION_MAX_ARTICLES_PER_SOURCE
                )

                fetched_count = len(articles)
                new_count = 0
                dup_count = 0

                for article in articles:
                    if article.source_url in self._seen_urls:
                        dup_count += 1
                        continue

                    # Mark as seen
                    self._seen_urls.add(article.source_url)

                    # Publish to Kafka
                    message = {
                        "title": article.title,
                        "content": article.content,
                        "source": article.source,
                        "source_url": article.source_url,
                        "published_at": article.published_at.isoformat() if article.published_at else None,
                        "metadata": article.metadata,
                    }

                    if self.process_callback:
                        try:
                            await self.process_callback(message)
                        except Exception as p_exc:
                            self._logger.error("callback_processing_failed", url=article.source_url, error=str(p_exc))
                    else:
                        try:
                            await produce_message(
                                topic=KafkaTopic.RAW_ARTICLES,
                                value=message,
                                key=article.source_url,
                            )
                        except Exception as k_exc:
                            self._logger.warning("kafka_produce_skipped", url=article.source_url, error=str(k_exc))
                    new_count += 1

                total_fetched += fetched_count
                total_new += new_count
                total_duplicates += dup_count

                source_stats.append({
                    "source": source.source_name,
                    "fetched": fetched_count,
                    "new": new_count,
                    "duplicates": dup_count,
                })

                self._logger.info(
                    "source_ingested",
                    source=source.source_name,
                    fetched=fetched_count,
                    new=new_count,
                    duplicates=dup_count,
                )

            except Exception as exc:
                error_msg = f"{source.source_name}: {exc}"
                errors.append(error_msg)
                self._logger.error(
                    "source_ingestion_failed",
                    source=source.source_name,
                    error=str(exc),
                )

        result = {
            "total_fetched": total_fetched,
            "total_new": total_new,
            "total_duplicates": total_duplicates,
            "sources": source_stats,
            "errors": errors,
        }

        self._logger.info(
            "ingestion_complete",
            total_fetched=total_fetched,
            total_new=total_new,
            total_duplicates=total_duplicates,
        )

        return result

    async def add_seen_urls(self, urls: set[str]) -> None:
        """Add URLs to the deduplication set (e.g., from database on startup).

        Args:
            urls: Set of already-known article URLs.
        """
        self._seen_urls.update(urls)
        self._logger.info("seen_urls_loaded", count=len(urls))

    def register_source(self, source: BaseSource) -> None:
        """Register an additional source adapter at runtime.

        Args:
            source: A BaseSource subclass instance.
        """
        self._sources.append(source)
        self._logger.info("source_registered", source=source.source_name)
