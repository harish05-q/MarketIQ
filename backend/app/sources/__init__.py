"""RSS feed source adapters."""

from app.sources.base_source import BaseSource, RawArticle
from app.sources.investing_com import InvestingComSource
from app.sources.marketwatch import MarketWatchSource
from app.sources.reuters import ReutersSource
from app.sources.yahoo_finance import YahooFinanceSource

__all__ = [
    "BaseSource",
    "InvestingComSource",
    "MarketWatchSource",
    "RawArticle",
    "ReutersSource",
    "YahooFinanceSource",
]
