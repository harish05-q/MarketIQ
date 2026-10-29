"""Event detection agent: detects market events from articles via LLM."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.agents.base_agent import BaseAgent
from app.core.logging import get_logger

logger = get_logger(__name__)


class DetectedEvent(BaseModel):
    """A single detected market event."""

    event_type: str = Field(
        description="Event type: earnings, acquisition, merger, ipo, layoffs, product_launch, regulation, legal, partnership, leadership_change, bankruptcy, stock_split, dividend, funding, expansion, recall, sanctions, policy_change, market_crash, other"
    )
    severity: str = Field(
        description="Severity: low, medium, high, critical",
        default="medium",
    )
    confidence: float = Field(
        description="Detection confidence 0.0-1.0",
        ge=0.0,
        le=1.0,
        default=0.7,
    )
    affected_entities: list[str] = Field(
        description="Names of entities affected by this event",
        default_factory=list,
    )
    affected_sectors: list[str] = Field(
        description="Sectors affected by this event",
        default_factory=list,
    )
    description: str = Field(
        description="Brief description of the event",
        default="",
    )


class EventDetectionOutput(BaseModel):
    """Structured output from the event detection LLM call."""

    events: list[DetectedEvent] = Field(
        description="List of detected market events",
        default_factory=list,
    )
    has_events: bool = Field(
        description="Whether any market events were detected",
        default=False,
    )


class EventDetectionAgent(BaseAgent):
    """Detects market events (earnings, acquisitions, layoffs, etc.) from articles.

    Input: Article title and content.
    Output: List of detected events with type, severity, affected entities/sectors.
    """

    @property
    def agent_name(self) -> str:
        return "EventDetectionAgent"

    @property
    def system_prompt(self) -> str:
        return """You are a financial event detection expert. Analyze the given article and identify any significant market events.

Return a JSON response with this exact structure:

{
    "events": [
        {
            "event_type": "earnings",
            "severity": "high",
            "confidence": 0.92,
            "affected_entities": ["Apple Inc."],
            "affected_sectors": ["Technology"],
            "description": "Apple reported Q3 earnings beating analyst expectations"
        }
    ],
    "has_events": true
}

EVENT TYPES: earnings, acquisition, merger, ipo, layoffs, product_launch, regulation, legal, partnership, leadership_change, bankruptcy, stock_split, dividend, funding, expansion, recall, sanctions, policy_change, market_crash, other

SEVERITY GUIDE:
- critical: Market-moving events affecting multiple sectors or major indices
- high: Significant events affecting large companies or entire sectors
- medium: Notable events with moderate market impact
- low: Minor events with limited market implications

RULES:
1. Only detect events that are explicitly described in the article.
2. Do not infer events that aren't clearly stated.
3. A single article may contain multiple events.
4. Set has_events to false if no significant market events are found.
5. Return ONLY valid JSON, no additional text."""

    async def process(self, data: dict[str, Any]) -> EventDetectionOutput:
        """Detect market events in the given article data.

        Args:
            data: Dictionary with 'title' and 'content' keys.

        Returns:
            EventDetectionOutput with list of detected events.
        """
        title = data.get("title", "")
        content = data.get("content", "")

        max_length = 5000
        if len(content) > max_length:
            content = content[:max_length] + "..."

        user_message = f"ARTICLE TITLE: {title}\n\nARTICLE CONTENT:\n{content}"

        fallback = EventDetectionOutput(events=[], has_events=False)

        result = await self._call_llm_with_fallback(
            user_message=user_message,
            output_schema=EventDetectionOutput,
            fallback=fallback,
        )

        self._logger.info(
            "events_detected",
            title=title[:80],
            event_count=len(result.events),
            has_events=result.has_events,
        )

        return result
