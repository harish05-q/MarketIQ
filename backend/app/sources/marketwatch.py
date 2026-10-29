"""MarketWatch RSS feed source adapter."""

from __future__ import annotations

from app.core.constants import SourceName
from app.sources.base_source import BaseSource


class MarketWatchSource(BaseSource):
    """Adapter for MarketWatch RSS news feeds.

    MarketWatch provides feeds for top stories, market pulse,
    and breaking market news.
    """

    @property
    def source_name(self) -> str:
        """Return the canonical source name."""
        return SourceName.MARKETWATCH

    @property
    def feed_urls(self) -> list[str]:
        """MarketWatch RSS feed URLs."""
        return [
            "https://feeds.marketwatch.com/marketwatch/topstories/",
            "https://feeds.marketwatch.com/marketwatch/marketpulse/",
            "https://feeds.marketwatch.com/marketwatch/StockstoWatch/",
        ]
