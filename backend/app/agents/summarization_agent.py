"""Summarization agent: generates article summaries and key takeaways via LLM."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.agents.base_agent import BaseAgent
from app.core.logging import get_logger

logger = get_logger(__name__)


class SummaryOutput(BaseModel):
    """Structured output from the summarization LLM call."""

    summary: str = Field(description="Concise 2-3 sentence summary of the article")
    key_takeaways: list[str] = Field(
        description="3-5 key takeaways from the article",
        default_factory=list,
    )
    market_relevance: str = Field(
        description="Brief statement on market relevance",
        default="",
    )


class SummarizationAgent(BaseAgent):
    """Generates concise summaries and key takeaways for articles using LLM.

    Input: Article title and content.
    Output: Summary, key takeaways, and market relevance statement.
    """

    @property
    def agent_name(self) -> str:
        return "SummarizationAgent"

    @property
    def system_prompt(self) -> str:
        return """You are a financial news summarization expert. Given an article title and content, produce a JSON response with the following structure:

{
    "summary": "A concise 2-3 sentence summary capturing the key information",
    "key_takeaways": ["takeaway 1", "takeaway 2", "takeaway 3"],
    "market_relevance": "Brief statement on how this relates to financial markets"
}

RULES:
1. The summary should be factual and objective, 2-3 sentences maximum.
2. Include 3-5 key takeaways as bullet points.
3. Focus on financially relevant information: numbers, dates, companies, market impact.
4. Do not add speculation or opinions.
5. Return ONLY valid JSON, no additional text."""

    async def process(self, data: dict[str, Any]) -> SummaryOutput:
        """Generate a summary for the given article data.

        Args:
            data: Dictionary with 'title' and 'content' keys.

        Returns:
            SummaryOutput with summary, key_takeaways, and market_relevance.
        """
        title = data.get("title", "")
        content = data.get("content", "")

        # Truncate content to avoid exceeding context limits
        max_content_length = 6000
        if len(content) > max_content_length:
            content = content[:max_content_length] + "..."

        user_message = f"ARTICLE TITLE: {title}\n\nARTICLE CONTENT:\n{content}"

        fallback = SummaryOutput(
            summary=f"Article about: {title}",
            key_takeaways=[title],
            market_relevance="Market relevance could not be determined.",
        )

        result = await self._call_llm_with_fallback(
            user_message=user_message,
            output_schema=SummaryOutput,
            fallback=fallback,
        )

        self._logger.info(
            "article_summarized",
            title=title[:80],
            summary_length=len(result.summary),
            takeaway_count=len(result.key_takeaways),
        )

        return result
