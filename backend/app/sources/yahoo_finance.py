"""Yahoo Finance RSS feed source adapter."""

from __future__ import annotations

from app.core.constants import SourceName
from app.sources.base_source import BaseSource


class YahooFinanceSource(BaseSource):
    """Adapter for Yahoo Finance RSS news feeds.

    Yahoo Finance provides RSS feeds for market news, sector-specific
    coverage, and trending financial topics.
    """

    @property
    def source_name(self) -> str:
        """Return the canonical source name."""
        return SourceName.YAHOO_FINANCE

    @property
    def feed_urls(self) -> list[str]:
        """Yahoo Finance RSS feed URLs."""
        return [
            "https://finance.yahoo.com/news/rssindex",
            "https://finance.yahoo.com/rss/topstories",
            "https://finance.yahoo.com/rss/industry?s=technology",
        ]
