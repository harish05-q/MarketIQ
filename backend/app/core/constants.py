"""Application-wide constants and enumerations."""

from __future__ import annotations

from enum import StrEnum


# ── Kafka Topics ─────────────────────────────────────────────────────────────

class KafkaTopic(StrEnum):
    """Kafka topic names used throughout the pipeline."""

    RAW_ARTICLES = "raw-articles"
    SUMMARIZED_ARTICLES = "summarized-articles"
    ENRICHED_ARTICLES = "enriched-articles"
    EVENTS = "events"


# ── Sentiment ────────────────────────────────────────────────────────────────

class SentimentLabel(StrEnum):
    """Allowed sentiment classification labels."""

    VERY_BULLISH = "very_bullish"
    BULLISH = "bullish"
    NEUTRAL = "neutral"
    BEARISH = "bearish"
    VERY_BEARISH = "very_bearish"


# ── Entity Types ─────────────────────────────────────────────────────────────

class EntityType(StrEnum):
    """Categories of named entities extracted from articles."""

    COMPANY = "company"
    PERSON = "person"
    SECTOR = "sector"
    INDEX = "index"
    COUNTRY = "country"
    COMMODITY = "commodity"
    CURRENCY = "currency"
    CRYPTO = "crypto"


# ── Event Types ──────────────────────────────────────────────────────────────

class EventType(StrEnum):
    """Market event categories detected by the event agent."""

    EARNINGS = "earnings"
    ACQUISITION = "acquisition"
    MERGER = "merger"
    IPO = "ipo"
    LAYOFFS = "layoffs"
    PRODUCT_LAUNCH = "product_launch"
    REGULATION = "regulation"
    LEGAL = "legal"
    PARTNERSHIP = "partnership"
    LEADERSHIP_CHANGE = "leadership_change"
    BANKRUPTCY = "bankruptcy"
    STOCK_SPLIT = "stock_split"
    DIVIDEND = "dividend"
    FUNDING = "funding"
    EXPANSION = "expansion"
    RECALL = "recall"
    SANCTIONS = "sanctions"
    POLICY_CHANGE = "policy_change"
    MARKET_CRASH = "market_crash"
    OTHER = "other"


# ── Event Severity ───────────────────────────────────────────────────────────

class EventSeverity(StrEnum):
    """Severity levels for detected market events."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ── Narrative Momentum ──────────────────────────────────────────────────────

class NarrativeMomentum(StrEnum):
    """Trend direction of a narrative cluster."""

    RISING = "rising"
    STABLE = "stable"
    DECLINING = "declining"


# ── Briefing Types ──────────────────────────────────────────────────────────

class BriefingType(StrEnum):
    """Types of automated market briefings."""

    MORNING = "morning"
    DAILY = "daily"
    WEEKLY = "weekly"


# ── Source Names ─────────────────────────────────────────────────────────────

class SourceName(StrEnum):
    """Canonical names for supported RSS feed sources."""

    REUTERS = "reuters"
    YAHOO_FINANCE = "yahoo_finance"
    MARKETWATCH = "marketwatch"
    INVESTING_COM = "investing_com"


# ── Pagination Defaults ─────────────────────────────────────────────────────

DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# ── Embedding ────────────────────────────────────────────────────────────────

EMBEDDING_DIMENSION = 768
