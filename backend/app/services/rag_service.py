"""RAG (Retrieval-Augmented Generation) service for chat functionality."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from app.config import get_settings
from app.core.exceptions import LLMError, VectorDBError
from app.core.logging import get_logger
from app.infrastructure.embeddings import embed_query
from app.infrastructure.qdrant_client import search_similar
from app.schemas.chat import ChatResponseData, Citation

logger = get_logger(__name__)

RAG_SYSTEM_PROMPT = """You are MarketIQ, an AI market intelligence assistant. You answer questions about financial markets, companies, and economic events based on the provided article context.

RULES:
1. Only use information from the provided article context to answer questions.
2. If the context doesn't contain enough information, say so honestly.
3. Always cite your sources by referencing article titles.
4. Be concise, professional, and data-driven in your responses.
5. If asked about specific numbers or dates, only provide them if they appear in the context.
6. Provide balanced analysis considering multiple viewpoints when available.

CONTEXT FROM RECENT ARTICLES:
{context}

Answer the user's question based on the above context. Include specific citations where appropriate."""


class RAGService:
    """Retrieval-Augmented Generation service for answering market questions.

    Pipeline: Question → Embed → Qdrant similarity search → Retrieve
    article context → LLM synthesis with citations → Response.
    """

    def __init__(self) -> None:
        settings = get_settings()
        self.llm = ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model=settings.GROQ_MODEL,
            temperature=0.2,
            max_tokens=settings.GROQ_MAX_TOKENS,
        )
        self.top_k = settings.RAG_TOP_K
        self.score_threshold = settings.RAG_SCORE_THRESHOLD

    async def answer_question(
        self,
        question: str,
        conversation_id: UUID | None = None,
    ) -> ChatResponseData:
        """Process a user question through the RAG pipeline.

        Args:
            question: The user's question.
            conversation_id: Optional conversation ID for context continuity.

        Returns:
            ChatResponseData with answer, citations, and confidence.

        Raises:
            LLMError: If the LLM call fails.
            VectorDBError: If vector search fails.
        """
        conv_id = conversation_id or uuid4()

        logger.info("rag_query_start", question=question[:100], conversation_id=str(conv_id))

        # Step 1: Embed the question
        try:
            query_vector = await embed_query(question)
        except Exception as exc:
            logger.error("rag_embedding_failed", error=str(exc))
            raise LLMError(f"Failed to embed query: {exc}") from exc

        # Step 2: Search Qdrant for similar articles
        try:
            search_results = await search_similar(
                query_vector=query_vector,
                top_k=self.top_k,
                score_threshold=self.score_threshold,
            )
        except VectorDBError:
            # Return a graceful response if vector search is unavailable
            search_results = []
            logger.warning("rag_vector_search_unavailable")

        # Step 3: Build context from search results
        context_parts: list[str] = []
        citations: list[Citation] = []

        for result in search_results:
            payload = result.get("payload", {})
            title = payload.get("title", "Unknown")
            content = payload.get("content", "")
            source = payload.get("source", "Unknown")
            source_url = payload.get("source_url", "")

            # Truncate content to avoid exceeding context window
            truncated_content = content[:1500] if len(content) > 1500 else content

            context_parts.append(
                f"[Article: {title}]\nSource: {source}\n{truncated_content}\n"
            )
            citations.append(
                Citation(
                    article_id=result.get("id", ""),
                    title=title,
                    source=source,
                    source_url=source_url,
                    relevance_score=round(result.get("score", 0.0), 4),
                    snippet=truncated_content[:300],
                )
            )

        # Step 4: Build prompt and call LLM
        if context_parts:
            context_text = "\n---\n".join(context_parts)
        else:
            context_text = "No relevant articles found in the database. Please provide a general market intelligence response and note that specific data is not available."

        system_prompt = RAG_SYSTEM_PROMPT.format(context=context_text)

        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=question),
            ]
            response = await self.llm.ainvoke(messages)
            answer = response.content
        except Exception as exc:
            logger.error("rag_llm_failed", error=str(exc))
            raise LLMError(f"LLM failed to generate answer: {exc}") from exc

        # Step 5: Calculate confidence based on search results quality
        if citations:
            avg_score = sum(c.relevance_score for c in citations) / len(citations)
            confidence = min(avg_score * 1.2, 1.0)  # Slight boost, capped at 1.0
        else:
            confidence = 0.1  # Low confidence when no context found

        logger.info(
            "rag_query_complete",
            conversation_id=str(conv_id),
            num_citations=len(citations),
            confidence=round(confidence, 4),
        )

        return ChatResponseData(
            conversation_id=conv_id,
            answer=answer,
            citations=citations,
            confidence=round(confidence, 4),
            generated_at=datetime.utcnow(),
        )
