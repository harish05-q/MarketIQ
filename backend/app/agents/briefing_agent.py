"""Market briefing agent: generates morning/daily/weekly briefings."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.agents.base_agent import BaseAgent
from app.core.logging import get_logger

logger = get_logger(__name__)


class BriefingSection(BaseModel):
    """A section within a generated briefing."""

    title: str = Field(description="Section title")
    content: str = Field(description="Section content")
    key_points: list[str] = Field(
        description="Key bullet points for this section",
        default_factory=list,
    )


class BriefingOutput(BaseModel):
    """Structured output from the briefing generation LLM call."""

    content: str = Field(description="Full briefing text")
    sections: list[BriefingSection] = Field(
        description="Structured sections of the briefing",
        default_factory=list,
    )


class MarketBriefingAgent(BaseAgent):
    """Generates structured market briefings (morning, daily, weekly).

    Input: Recent articles, events, narratives, and briefing type.
    Output: Comprehensive briefing with sections and key points.
    """

    @property
    def agent_name(self) -> str:
        return "MarketBriefingAgent"

    @property
    def system_prompt(self) -> str:
        return """You are a senior market analyst writing professional market briefings. Generate a comprehensive briefing based on the provided market data.

Return a JSON response with this exact structure:

{
    "content": "Full briefing text as a cohesive report...",
    "sections": [
        {
            "title": "Market Overview",
            "content": "Detailed section content...",
            "key_points": ["Point 1", "Point 2"]
        },
        {
            "title": "Key Events",
            "content": "...",
            "key_points": ["..."]
        }
    ]
}

BRIEFING SECTIONS TO INCLUDE:
1. Market Overview – High-level summary of market conditions
2. Key Events – Most significant events in the period
3. Sector Analysis – Performance and trends by sector
4. Notable Companies – Companies making headlines
5. Trending Narratives – Emerging themes and stories
6. Risk Factors – Potential risks and concerns
7. Outlook – Forward-looking analysis

RULES:
1. Be professional, concise, and data-driven.
2. Reference specific articles and events where possible.
3. Provide balanced analysis considering multiple perspectives.
4. Include actionable insights where appropriate.
5. Adjust depth based on briefing type (morning=concise, daily=moderate, weekly=comprehensive).
6. Return ONLY valid JSON, no additional text."""

    async def process(self, data: dict[str, Any]) -> BriefingOutput:
        """Generate a market briefing from provided data.

        Args:
            data: Dictionary with:
                - briefing_type: 'morning', 'daily', or 'weekly'
                - articles: List of recent article dicts
                - events: List of recent event dicts
                - narratives: List of active narrative dicts
                - sentiment_summary: Overall market sentiment info

        Returns:
            BriefingOutput with full content and structured sections.
        """
        briefing_type = data.get("briefing_type", "daily")
        articles = data.get("articles", [])
        events = data.get("events", [])
        narratives = data.get("narratives", [])
        sentiment_summary = data.get("sentiment_summary", {})

        # Build context for the LLM
        context_parts = [f"BRIEFING TYPE: {briefing_type.upper()}\n"]

        # Sentiment overview
        if sentiment_summary:
            context_parts.append(
                f"MARKET SENTIMENT: Average score: {sentiment_summary.get('average_score', 0)}, "
                f"Distribution: {sentiment_summary.get('distribution', {})}\n"
            )

        # Top articles
        if articles:
            context_parts.append("TOP ARTICLES:")
            for i, article in enumerate(articles[:15]):
                title = article.get("title", "")
                source = article.get("source", "")
                sentiment = article.get("sentiment", "")
                summary = article.get("summary", "")[:200]
                context_parts.append(f"  {i+1}. [{source}] {title} (Sentiment: {sentiment})")
                if summary:
                    context_parts.append(f"     Summary: {summary}")
            context_parts.append("")

        # Events
        if events:
            context_parts.append("KEY EVENTS:")
            for event in events[:10]:
                event_type = event.get("event_type", "")
                severity = event.get("severity", "")
                affected = event.get("affected_entities", [])
                context_parts.append(
                    f"  - {event_type} (Severity: {severity}) "
                    f"Affecting: {', '.join(affected) if affected else 'N/A'}"
                )
            context_parts.append("")

        # Narratives
        if narratives:
            context_parts.append("ACTIVE NARRATIVES:")
            for narrative in narratives[:5]:
                title = narrative.get("title", "")
                momentum = narrative.get("momentum", "")
                trend_score = narrative.get("trend_score", 0)
                context_parts.append(
                    f"  - {title} (Momentum: {momentum}, Trend Score: {trend_score})"
                )
            context_parts.append("")

        user_message = "\n".join(context_parts)

        # Adjust fallback based on type
        type_labels = {
            "morning": "Morning Market Briefing",
            "daily": "Daily Market Summary",
            "weekly": "Weekly Market Review",
        }

        fallback = BriefingOutput(
            content=f"{type_labels.get(briefing_type, 'Market Briefing')}: "
                    f"Insufficient data to generate a comprehensive briefing. "
                    f"Analyzed {len(articles)} articles and {len(events)} events.",
            sections=[
                BriefingSection(
                    title="Overview",
                    content="Market data is being collected. A comprehensive briefing will be available once more data is processed.",
                    key_points=["Data collection in progress"],
                )
            ],
        )

        result = await self._call_llm_with_fallback(
            user_message=user_message,
            output_schema=BriefingOutput,
            fallback=fallback,
        )

        self._logger.info(
            "briefing_generated",
            briefing_type=briefing_type,
            section_count=len(result.sections),
            content_length=len(result.content),
        )

        return result
