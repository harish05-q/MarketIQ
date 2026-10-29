"""Impact scoring agent: calculates 0-100 impact score for articles."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.agents.base_agent import BaseAgent
from app.core.logging import get_logger

logger = get_logger(__name__)

# Source authority weights (higher = more authoritative)
SOURCE_AUTHORITY: dict[str, float] = {
    "reuters": 0.95,
    "yahoo_finance": 0.80,
    "marketwatch": 0.85,
    "investing_com": 0.75,
}

# Event severity multipliers
SEVERITY_MULTIPLIER: dict[str, float] = {
    "critical": 1.5,
    "high": 1.2,
    "medium": 1.0,
    "low": 0.7,
}


class ImpactScoreOutput(BaseModel):
    """Structured impact score output."""

    impact_score: float = Field(
        description="Overall impact score 0-100",
        ge=0.0,
        le=100.0,
    )
    components: dict[str, float] = Field(
        description="Breakdown of scoring components",
        default_factory=dict,
    )
    reasoning: str = Field(
        description="Brief explanation of the impact assessment",
        default="",
    )


class ImpactScoringAgent(BaseAgent):
    """Calculates a 0-100 impact score based on multiple factors.

    Scoring formula combines:
    - Source authority (20%): Credibility of the news source
    - Entity importance (25%): Significance of mentioned entities
    - Sentiment magnitude (20%): Strength of sentiment signal
    - Event severity (25%): Severity of detected events
    - Recency (10%): How recent the article is

    This agent primarily uses rule-based scoring but can optionally
    consult the LLM for entity importance assessment.
    """

    @property
    def agent_name(self) -> str:
        return "ImpactScoringAgent"

    @property
    def system_prompt(self) -> str:
        return """You are a financial impact assessment expert. Given article details, assess the market impact.

Return JSON:
{
    "impact_score": 75.0,
    "components": {
        "source_authority": 19.0,
        "entity_importance": 25.0,
        "sentiment_magnitude": 15.0,
        "event_severity": 16.0
    },
    "reasoning": "Brief explanation"
}

Return ONLY valid JSON."""

    async def process(self, data: dict[str, Any]) -> ImpactScoreOutput:
        """Calculate impact score for an article using a weighted formula.

        Args:
            data: Dictionary with article attributes:
                - source: Source name
                - sentiment_score: Float -1.0 to 1.0
                - events: List of event dicts with 'severity'
                - entities: List of entity dicts
                - title: Article title
                - content: Article content

        Returns:
            ImpactScoreOutput with score, components, and reasoning.
        """
        source = data.get("source", "")
        sentiment_score = data.get("sentiment_score", 0.0) or 0.0
        events = data.get("events", [])
        entities = data.get("entities", [])

        # 1. Source authority (0-20 points)
        authority = SOURCE_AUTHORITY.get(source, 0.6)
        source_score = authority * 20.0

        # 2. Entity importance (0-25 points)
        entity_count = len(entities)
        entity_types = {e.get("type", "") for e in entities} if entities else set()

        # More entity types and entities = higher importance
        type_diversity_score = min(len(entity_types) / 4.0, 1.0) * 15.0
        entity_volume_score = min(entity_count / 5.0, 1.0) * 10.0
        entity_score = type_diversity_score + entity_volume_score

        # 3. Sentiment magnitude (0-20 points)
        # Higher magnitude (regardless of direction) = more impactful
        sentiment_magnitude = abs(sentiment_score)
        sentiment_component = sentiment_magnitude * 20.0

        # 4. Event severity (0-25 points)
        event_score = 0.0
        if events:
            max_severity_multiplier = max(
                SEVERITY_MULTIPLIER.get(e.get("severity", "low"), 0.7)
                for e in events
            )
            event_count_factor = min(len(events) / 3.0, 1.0)
            event_score = max_severity_multiplier * event_count_factor * 25.0

        # 5. Recency bonus (0-10 points) – applied as flat 7 since we process near-realtime
        recency_score = 7.0

        # Total impact score
        total = source_score + entity_score + sentiment_component + event_score + recency_score
        total = min(max(total, 0.0), 100.0)

        components = {
            "source_authority": round(source_score, 2),
            "entity_importance": round(entity_score, 2),
            "sentiment_magnitude": round(sentiment_component, 2),
            "event_severity": round(event_score, 2),
            "recency": round(recency_score, 2),
        }

        reasoning = (
            f"Source '{source}' (authority: {authority:.0%}), "
            f"{entity_count} entities across {len(entity_types)} types, "
            f"sentiment magnitude {sentiment_magnitude:.2f}, "
            f"{len(events)} events detected."
        )

        self._logger.info(
            "impact_scored",
            title=data.get("title", "")[:80],
            impact_score=round(total, 2),
        )

        return ImpactScoreOutput(
            impact_score=round(total, 2),
            components=components,
            reasoning=reasoning,
        )
