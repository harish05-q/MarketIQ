"""Investing.com RSS feed source adapter."""

from __future__ import annotations

from app.core.constants import SourceName
from app.sources.base_source import BaseSource


class InvestingComSource(BaseSource):
    """Adapter for Investing.com RSS news feeds.

    Investing.com provides feeds covering a wide range of financial
    markets including stocks, forex, commodities, and crypto.
    """

    @property
    def source_name(self) -> str:
        """Return the canonical source name."""
        return SourceName.INVESTING_COM

    @property
    def feed_urls(self) -> list[str]:
        """Investing.com RSS feed URLs."""
        return [
            "https://www.investing.com/rss/news.rss",
            "https://www.investing.com/rss/news_14.rss",  # Economy
            "https://www.investing.com/rss/news_25.rss",  # Stocks
        ]
