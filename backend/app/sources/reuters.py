"""Reuters RSS feed source adapter."""

from __future__ import annotations

from app.core.constants import SourceName
from app.sources.base_source import BaseSource


class ReutersSource(BaseSource):
    """Adapter for Reuters RSS news feeds.

    Reuters provides structured RSS feeds covering world business news,
    technology, and markets.
    """

    @property
    def source_name(self) -> str:
        """Return the canonical source name."""
        return SourceName.REUTERS

    @property
    def feed_urls(self) -> list[str]:
        """Reuters RSS feed URLs for business and market news."""
        return [
            "https://www.reutersagency.com/feed/?taxonomy=best-sectors&post_type=best",
            "https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best",
            "https://www.reutersagency.com/feed/?best-topics=tech&post_type=best",
        ]
