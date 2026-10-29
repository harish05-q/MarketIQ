"""Chat / RAG Pydantic schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """A single message in a conversation."""

    role: Literal["user", "assistant"] = "user"
    content: str


class ChatRequest(BaseModel):
    """Request body for the RAG chat endpoint."""

    question: str = Field(..., min_length=3, max_length=2000, description="User question")
    conversation_id: UUID | None = Field(None, description="Optional conversation ID for context")


class Citation(BaseModel):
    """A source citation from the RAG pipeline."""

    article_id: str
    title: str
    source: str
    source_url: str
    relevance_score: float = Field(ge=0.0, le=1.0)
    snippet: str = ""


class ChatResponse(BaseModel):
    """Response from the RAG chat endpoint."""

    success: bool = True
    data: ChatResponseData


class ChatResponseData(BaseModel):
    """Chat response payload with answer and citations."""

    conversation_id: UUID = Field(default_factory=uuid4)
    answer: str
    citations: list[Citation] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    generated_at: datetime = Field(default_factory=datetime.utcnow)
