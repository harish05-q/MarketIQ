"""Custom exception hierarchy for the MarketIQ application.

All business-logic and infrastructure exceptions inherit from
``MarketIQError`` so that a single catch-all handler can translate any
known error into a structured API response.
"""

from __future__ import annotations

from typing import Any


class MarketIQError(Exception):
    """Base exception for all MarketIQ application errors."""

    def __init__(
        self,
        message: str = "An unexpected error occurred",
        code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


# ── Resource Errors ─────────────────────────────────────────────────────────

class NotFoundError(MarketIQError):
    """Raised when a requested resource does not exist."""

    def __init__(self, resource: str = "Resource", resource_id: str | None = None) -> None:
        detail = f"{resource} not found"
        if resource_id:
            detail = f"{resource} with id '{resource_id}' not found"
        super().__init__(message=detail, code="NOT_FOUND", status_code=404)


class DuplicateError(MarketIQError):
    """Raised when attempting to create a resource that already exists."""

    def __init__(self, resource: str = "Resource", identifier: str | None = None) -> None:
        detail = f"{resource} already exists"
        if identifier:
            detail = f"{resource} '{identifier}' already exists"
        super().__init__(message=detail, code="DUPLICATE", status_code=409)


# ── Validation Errors ───────────────────────────────────────────────────────

class ValidationError(MarketIQError):
    """Raised when input data fails business-logic validation."""

    def __init__(self, message: str = "Validation failed", details: dict[str, Any] | None = None) -> None:
        super().__init__(message=message, code="VALIDATION_ERROR", status_code=422, details=details)


# ── Infrastructure Errors ───────────────────────────────────────────────────

class DatabaseError(MarketIQError):
    """Raised when a database operation fails."""

    def __init__(self, message: str = "Database operation failed") -> None:
        super().__init__(message=message, code="DATABASE_ERROR", status_code=500)


class KafkaError(MarketIQError):
    """Raised when a Kafka operation fails."""

    def __init__(self, message: str = "Kafka operation failed") -> None:
        super().__init__(message=message, code="KAFKA_ERROR", status_code=500)


class VectorDBError(MarketIQError):
    """Raised when a Qdrant operation fails."""

    def __init__(self, message: str = "Vector database operation failed") -> None:
        super().__init__(message=message, code="VECTOR_DB_ERROR", status_code=500)


class EmbeddingError(MarketIQError):
    """Raised when text embedding fails."""

    def __init__(self, message: str = "Embedding generation failed") -> None:
        super().__init__(message=message, code="EMBEDDING_ERROR", status_code=500)


# ── LLM Errors ──────────────────────────────────────────────────────────────

class LLMError(MarketIQError):
    """Raised when an LLM call fails."""

    def __init__(self, message: str = "LLM operation failed") -> None:
        super().__init__(message=message, code="LLM_ERROR", status_code=502)


class AgentError(MarketIQError):
    """Raised when an agent processing step fails."""

    def __init__(self, agent_name: str, message: str = "Agent processing failed") -> None:
        super().__init__(
            message=f"[{agent_name}] {message}",
            code="AGENT_ERROR",
            status_code=500,
        )


# ── External Service Errors ─────────────────────────────────────────────────

class ExternalServiceError(MarketIQError):
    """Raised when an external service (RSS feed, API) is unreachable."""

    def __init__(self, service: str, message: str = "External service unavailable") -> None:
        super().__init__(
            message=f"[{service}] {message}",
            code="EXTERNAL_SERVICE_ERROR",
            status_code=502,
        )


class RateLimitError(MarketIQError):
    """Raised when rate limits are hit on external services."""

    def __init__(self, service: str = "Service") -> None:
        super().__init__(
            message=f"Rate limit exceeded for {service}",
            code="RATE_LIMIT",
            status_code=429,
        )


class IngestionError(MarketIQError):
    """Raised when article ingestion fails."""

    def __init__(self, message: str = "Article ingestion failed") -> None:
        super().__init__(message=message, code="INGESTION_ERROR", status_code=500)
