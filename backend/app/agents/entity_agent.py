"""Entity extraction agent: extracts companies, people, sectors, and indices via LLM."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.agents.base_agent import BaseAgent
from app.core.logging import get_logger

logger = get_logger(__name__)


class ExtractedEntity(BaseModel):
    """A single extracted entity."""

    name: str = Field(description="Entity name")
    type: str = Field(description="Entity type: company, person, sector, index, country, commodity, currency, crypto")
    confidence: float = Field(description="Extraction confidence 0.0-1.0", ge=0.0, le=1.0, default=0.8)


class EntityExtractionOutput(BaseModel):
    """Structured output from the entity extraction LLM call."""

    entities: list[ExtractedEntity] = Field(
        description="List of extracted entities",
        default_factory=list,
    )


class EntityExtractionAgent(BaseAgent):
    """Extracts named entities (companies, people, sectors, indices) from articles.

    Input: Article title and content.
    Output: List of entities with type and confidence.
    """

    @property
    def agent_name(self) -> str:
        return "EntityExtractionAgent"

    @property
    def system_prompt(self) -> str:
        return """You are a financial named entity recognition expert. Extract all relevant entities from the given article.

Return a JSON response with this exact structure:

{
    "entities": [
        {"name": "Apple Inc.", "type": "company", "confidence": 0.95},
        {"name": "Tim Cook", "type": "person", "confidence": 0.90},
        {"name": "Technology", "type": "sector", "confidence": 0.85},
        {"name": "S&P 500", "type": "index", "confidence": 0.80}
    ]
}

ENTITY TYPES:
- company: Publicly traded or notable private companies (use official names)
- person: CEOs, executives, analysts, politicians relevant to markets
- sector: Industry sectors (Technology, Healthcare, Energy, Finance, etc.)
- index: Market indices (S&P 500, Nasdaq, Dow Jones, FTSE 100, etc.)
- country: Countries mentioned in economic/trade context
- commodity: Commodities (Oil, Gold, Silver, Natural Gas, etc.)
- currency: Currencies (USD, EUR, GBP, JPY, etc.)
- crypto: Cryptocurrencies (Bitcoin, Ethereum, etc.)

RULES:
1. Extract all financially relevant entities from the article.
2. Use official/full entity names when possible.
3. Assign confidence based on how clearly the entity is mentioned.
4. Do not include generic terms that aren't specific entities.
5. Return ONLY valid JSON, no additional text."""

    async def process(self, data: dict[str, Any]) -> EntityExtractionOutput:
        """Extract entities from the given article data.

        Args:
            data: Dictionary with 'title' and 'content' keys.

        Returns:
            EntityExtractionOutput with list of extracted entities.
        """
        title = data.get("title", "")
        content = data.get("content", "")

        max_length = 5000
        if len(content) > max_length:
            content = content[:max_length] + "..."

        user_message = f"ARTICLE TITLE: {title}\n\nARTICLE CONTENT:\n{content}"

        fallback = EntityExtractionOutput(entities=[])

        result = await self._call_llm_with_fallback(
            user_message=user_message,
            output_schema=EntityExtractionOutput,
            fallback=fallback,
        )

        self._logger.info(
            "entities_extracted",
            title=title[:80],
            entity_count=len(result.entities),
            entity_types=[e.type for e in result.entities],
        )

        return result
