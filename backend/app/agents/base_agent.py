"""Base agent abstraction for all AI agents in the pipeline."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, TypeVar

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import get_settings
from app.core.exceptions import AgentError, LLMError
from app.core.logging import get_logger

T = TypeVar("T", bound=BaseModel)

logger = get_logger(__name__)


class BaseAgent(ABC):
    """Abstract base class for AI pipeline agents.

    Provides common LLM interaction patterns, structured output parsing,
    and retry logic. Subclasses implement ``agent_name``, ``system_prompt``,
    and ``process`` to define their specific behavior.
    """

    def __init__(self) -> None:
        settings = get_settings()
        self.llm = ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model=settings.GROQ_MODEL,
            temperature=settings.GROQ_TEMPERATURE,
            max_tokens=settings.GROQ_MAX_TOKENS,
        )
        self._logger = get_logger(self.__class__.__name__, agent=self.agent_name)

    @property
    @abstractmethod
    def agent_name(self) -> str:
        """Unique name identifying this agent."""
        ...

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """System prompt defining the agent's role and output format."""
        ...

    @abstractmethod
    async def process(self, data: Any) -> Any:
        """Process input data and return enriched output.

        Args:
            data: Input data specific to this agent.

        Returns:
            Processed/enriched data.
        """
        ...

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        reraise=True,
    )
    async def _call_llm(self, user_message: str) -> str:
        """Call the LLM with retry logic.

        Args:
            user_message: The user/input message to send to the LLM.

        Returns:
            The LLM's response content as a string.

        Raises:
            LLMError: If all retry attempts fail.
        """
        try:
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=user_message),
            ]
            response = await self.llm.ainvoke(messages)
            return response.content
        except Exception as exc:
            self._logger.error(
                "llm_call_failed",
                agent=self.agent_name,
                error=str(exc),
            )
            raise LLMError(f"[{self.agent_name}] LLM call failed: {exc}") from exc

    async def _call_llm_structured(
        self, user_message: str, output_schema: type[T]
    ) -> T:
        """Call the LLM and parse the response into a structured Pydantic model.

        Uses the LLM's JSON output capability and validates against the
        provided schema.

        Args:
            user_message: The input message.
            output_schema: Pydantic model class to parse the output into.

        Returns:
            Parsed Pydantic model instance.

        Raises:
            AgentError: If parsing fails after LLM response.
        """
        import json

        raw_response = await self._call_llm(user_message)

        try:
            # Try to extract JSON from the response
            json_str = raw_response.strip()

            # Handle responses wrapped in markdown code blocks
            if json_str.startswith("```json"):
                json_str = json_str[7:]
            if json_str.startswith("```"):
                json_str = json_str[3:]
            if json_str.endswith("```"):
                json_str = json_str[:-3]
            json_str = json_str.strip()

            parsed_data = json.loads(json_str)
            return output_schema.model_validate(parsed_data)
        except (json.JSONDecodeError, Exception) as exc:
            self._logger.error(
                "structured_output_parse_failed",
                agent=self.agent_name,
                raw_response=raw_response[:500],
                error=str(exc),
            )
            raise AgentError(
                self.agent_name,
                f"Failed to parse structured output: {exc}",
            ) from exc

    async def _call_llm_with_fallback(
        self, user_message: str, output_schema: type[T], fallback: T
    ) -> T:
        """Call the LLM with structured output, returning a fallback on failure.

        Args:
            user_message: The input message.
            output_schema: Pydantic model class.
            fallback: Default value to return if LLM/parsing fails.

        Returns:
            Parsed model or fallback.
        """
        try:
            return await self._call_llm_structured(user_message, output_schema)
        except (LLMError, AgentError) as exc:
            self._logger.warning(
                "using_fallback",
                agent=self.agent_name,
                error=str(exc),
            )
            return fallback
