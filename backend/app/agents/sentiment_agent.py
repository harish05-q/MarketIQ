"""Sentiment agent: determines sentiment, score, confidence, and reasoning via LLM."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.agents.base_agent import BaseAgent
from app.core.logging import get_logger

logger = get_logger(__name__)


class SentimentOutput(BaseModel):
    """Structured output from the sentiment analysis LLM call."""

    sentiment: str = Field(
        description="Sentiment label: very_bullish, bullish, neutral, bearish, or very_bearish"
    )
    score: float = Field(
        description="Sentiment score from -1.0 (very bearish) to 1.0 (very bullish)",
        ge=-1.0,
        le=1.0,
    )
    confidence: float = Field(
        description="Confidence in the sentiment assessment from 0.0 to 1.0",
        ge=0.0,
        le=1.0,
    )
    reasoning: str = Field(
        description="Brief explanation of the sentiment assessment",
        default="",
    )


class SentimentAgent(BaseAgent):
    """Analyzes the sentiment of financial articles using LLM.

    Input: Article title and content (or summary).
    Output: Sentiment label, numeric score, confidence, and reasoning.
    """

    @property
    def agent_name(self) -> str:
        return "SentimentAgent"

    @property
    def system_prompt(self) -> str:
        return """You are a financial sentiment analysis expert. Analyze the given article and determine its market sentiment.

Return a JSON response with this exact structure:

{
    "sentiment": "one of: very_bullish, bullish, neutral, bearish, very_bearish",
    "score": 0.0,
    "confidence": 0.0,
    "reasoning": "Brief explanation"
}

SCORING GUIDE:
- very_bullish (0.75 to 1.0): Strongly positive news – major earnings beat, acquisitions, breakthroughs
- bullish (0.25 to 0.74): Positive news – growth, expansion, favorable reports  
- neutral (-0.24 to 0.24): Mixed or informational news with no clear market direction
- bearish (-0.74 to -0.25): Negative news – declines, losses, downgrades
- very_bearish (-1.0 to -0.75): Strongly negative – crashes, scandals, major losses

RULES:
1. Consider both the headline tone and the full content.
2. Look for financial keywords: revenue, profit, loss, growth, decline, beat, miss.
3. The confidence should reflect how clearly the sentiment is conveyed.
4. Return ONLY valid JSON, no additional text."""

    async def process(self, data: dict[str, Any]) -> SentimentOutput:
        """Analyze sentiment for the given article data.

        Args:
            data: Dictionary with 'title' and 'content' (or 'summary') keys.

        Returns:
            SentimentOutput with sentiment label, score, confidence, reasoning.
        """
        title = data.get("title", "")
        content = data.get("summary", data.get("content", ""))

        # Use summary if available, otherwise truncated content
        max_length = 4000
        if len(content) > max_length:
            content = content[:max_length] + "..."

        user_message = f"ARTICLE TITLE: {title}\n\nARTICLE CONTENT:\n{content}"

        fallback = SentimentOutput(
            sentiment="neutral",
            score=0.0,
            confidence=0.3,
            reasoning="Sentiment could not be determined automatically.",
        )

        result = await self._call_llm_with_fallback(
            user_message=user_message,
            output_schema=SentimentOutput,
            fallback=fallback,
        )

        self._logger.info(
            "sentiment_analyzed",
            title=title[:80],
            sentiment=result.sentiment,
            score=result.score,
            confidence=result.confidence,
        )

        return result
