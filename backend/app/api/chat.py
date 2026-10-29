"""Chat and RAG API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.dependencies import get_rag_service
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.rag_service import RAGService

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat_rag(
    request: ChatRequest,
    service: RAGService = Depends(get_rag_service),
) -> ChatResponse:
    """Ask MarketIQ questions using Retrieval-Augmented Generation (RAG)."""
    response_data = await service.answer_question(
        question=request.question,
        conversation_id=request.conversation_id,
    )
    return ChatResponse(
        success=True,
        data=response_data,
    )
