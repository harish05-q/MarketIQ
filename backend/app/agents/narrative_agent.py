"""Narrative detection agent: groups articles into themes and tracks trends."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Sequence

from pydantic import BaseModel, Field

from app.agents.base_agent import BaseAgent
from app.core.logging import get_logger

logger = get_logger(__name__)


class DetectedNarrative(BaseModel):
    """A detected narrative theme."""

    title: str = Field(description="Concise narrative title")
    description: str = Field(description="Description of the narrative theme")
    trend_score: float = Field(
        description="Trending score 0-100",
        ge=0.0,
        le=100.0,
        default=50.0,
    )
    momentum: str = Field(
        description="Momentum: rising, stable, declining",
        default="stable",
    )
    sentiment: str = Field(
        description="Overall sentiment of the narrative",
        default="neutral",
    )
    related_article_indices: list[int] = Field(
        description="Indices of articles in the input that belong to this narrative",
        default_factory=list,
    )


class NarrativeDetectionOutput(BaseModel):
    """Structured output from the narrative detection LLM call."""

    narratives: list[DetectedNarrative] = Field(
        description="List of detected narrative themes",
        default_factory=list,
    )


class NarrativeDetectionAgent(BaseAgent):
    """Groups articles into thematic narratives and tracks frequency/momentum/sentiment.

    Runs periodically to identify emerging themes across recent articles.

    Input: List of recent article summaries.
    Output: List of narrative themes with trend scores and momentum.
    """

    @property
    def agent_name(self) -> str:
        return "NarrativeDetectionAgent"

    @property
    def system_prompt(self) -> str:
        return """You are a market narrative detection expert. Given a list of recent article summaries, identify overarching themes and narratives.

Return a JSON response with this exact structure:

{
    "narratives": [
        {
            "title": "AI Infrastructure Boom",
            "description": "Multiple tech companies are investing heavily in AI infrastructure and data centers",
            "trend_score": 85.0,
            "momentum": "rising",
            "sentiment": "bullish",
            "related_article_indices": [0, 3, 7, 12]
        }
    ]
}

RULES:
1. Group articles that share common themes into narratives.
2. A narrative should represent a meaningful market trend or story.
3. Each narrative needs at least 2-3 related articles to be valid.
4. Assign trend_score based on how many articles and how significant the theme is (0-100).
5. Momentum: "rising" if the theme is gaining coverage, "declining" if fading, "stable" if consistent.
6. Sentiment should reflect the overall tone of articles in the narrative.
7. related_article_indices refer to the 0-indexed position of articles in the input list.
8. Limit to the top 5-10 most significant narratives.
9. Return ONLY valid JSON, no additional text."""

    async def process(self, data: dict[str, Any]) -> NarrativeDetectionOutput:
        """Detect narratives from a list of recent article summaries.

        Args:
            data: Dictionary with 'articles' key containing a list of article
                  dicts (each with 'title', 'summary', and optionally 'source').

        Returns:
            NarrativeDetectionOutput with list of detected narratives.
        """
        articles: list[dict[str, Any]] = data.get("articles", [])

        if len(articles) < 3:
            self._logger.info("insufficient_articles_for_narratives", count=len(articles))
            return NarrativeDetectionOutput(narratives=[])

        # Build a condensed representation of articles for the LLM
        article_summaries = []
        for i, article in enumerate(articles):
            title = article.get("title", "")
            summary = article.get("summary", article.get("content", ""))[:300]
            source = article.get("source", "")
            article_summaries.append(
                f"[{i}] ({source}) {title}: {summary}"
            )

        user_message = (
            f"Analyze these {len(articles)} recent articles and identify common narratives/themes:\n\n"
            + "\n\n".join(article_summaries)
        )

        fallback = NarrativeDetectionOutput(narratives=[])

        result = await self._call_llm_with_fallback(
            user_message=user_message,
            output_schema=NarrativeDetectionOutput,
            fallback=fallback,
        )

        self._logger.info(
            "narratives_detected",
            article_count=len(articles),
            narrative_count=len(result.narratives),
            narrative_titles=[n.title for n in result.narratives],
        )

        return result
