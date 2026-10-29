"""Qdrant vector database client wrapper."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    SearchParams,
    VectorParams,
)

from app.config import get_settings
from app.core.exceptions import VectorDBError
from app.core.logging import get_logger

logger = get_logger(__name__)

_client: QdrantClient | None = None


def get_qdrant_client() -> QdrantClient:
    """Return the global Qdrant client, creating it on first call."""
    global _client
    if _client is None:
        settings = get_settings()
        if settings.QDRANT_HOST == ":memory:":
            _client = QdrantClient(location=":memory:")
            logger.info("qdrant_client_created_in_memory")
        elif settings.QDRANT_HOST.startswith("http://") or settings.QDRANT_HOST.startswith("https://"):
            _client = QdrantClient(url=settings.QDRANT_HOST, api_key=settings.QDRANT_API_KEY, timeout=30)
            logger.info("qdrant_client_created_with_url", url=settings.QDRANT_HOST)
        else:
            _client = QdrantClient(
                host=settings.QDRANT_HOST,
                port=settings.QDRANT_PORT,
                grpc_port=settings.QDRANT_GRPC_PORT,
                api_key=settings.QDRANT_API_KEY,
                prefer_grpc=True,
                timeout=30,
            )
            logger.info("qdrant_client_created", host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
    return _client


async def ensure_collection_exists() -> None:
    """Create the articles vector collection if it does not already exist."""
    settings = get_settings()
    client = get_qdrant_client()
    collection_name = settings.QDRANT_COLLECTION_NAME

    try:
        collections = client.get_collections().collections
        existing_names = {c.name for c in collections}

        if collection_name not in existing_names:
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=settings.QDRANT_VECTOR_SIZE,
                    distance=Distance.COSINE,
                ),
            )
            # Create payload indices for filtering
            client.create_payload_index(
                collection_name=collection_name,
                field_name="source",
                field_schema="keyword",
            )
            client.create_payload_index(
                collection_name=collection_name,
                field_name="sentiment",
                field_schema="keyword",
            )
            client.create_payload_index(
                collection_name=collection_name,
                field_name="published_at",
                field_schema="datetime",
            )
            logger.info("qdrant_collection_created", collection=collection_name)
        else:
            logger.info("qdrant_collection_exists", collection=collection_name)
    except Exception as exc:
        logger.error("qdrant_collection_setup_error", error=str(exc))
        raise VectorDBError(f"Failed to ensure Qdrant collection: {exc}") from exc


async def upsert_vector(
    article_id: str,
    vector: list[float],
    payload: dict[str, Any],
) -> str:
    """Upsert a single vector with its metadata payload.

    Args:
        article_id: UUID string used as the point id.
        vector: Embedding vector of EMBEDDING_DIMENSION size.
        payload: Metadata to store alongside the vector.

    Returns:
        The article_id that was upserted.

    Raises:
        VectorDBError: If the upsert fails.
    """
    settings = get_settings()
    client = get_qdrant_client()

    try:
        client.upsert(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            points=[
                PointStruct(
                    id=article_id,
                    vector=vector,
                    payload=payload,
                )
            ],
        )
        logger.debug("qdrant_vector_upserted", article_id=article_id)
        return article_id
    except Exception as exc:
        logger.error("qdrant_upsert_error", article_id=article_id, error=str(exc))
        raise VectorDBError(f"Failed to upsert vector: {exc}") from exc


async def search_similar(
    query_vector: list[float],
    top_k: int | None = None,
    score_threshold: float | None = None,
    source_filter: str | None = None,
    sentiment_filter: str | None = None,
) -> list[dict[str, Any]]:
    """Search for similar articles by vector similarity.

    Args:
        query_vector: Query embedding vector.
        top_k: Number of results to return.
        score_threshold: Minimum similarity score.
        source_filter: Optional filter by source name.
        sentiment_filter: Optional filter by sentiment label.

    Returns:
        List of dicts with ``id``, ``score``, and ``payload`` keys.

    Raises:
        VectorDBError: If the search fails.
    """
    settings = get_settings()
    client = get_qdrant_client()

    top_k = top_k or settings.RAG_TOP_K
    score_threshold = score_threshold or settings.RAG_SCORE_THRESHOLD

    # Build filter conditions
    conditions = []
    if source_filter:
        conditions.append(FieldCondition(key="source", match=MatchValue(value=source_filter)))
    if sentiment_filter:
        conditions.append(FieldCondition(key="sentiment", match=MatchValue(value=sentiment_filter)))

    search_filter = Filter(must=conditions) if conditions else None

    try:
        results = client.search(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            query_vector=query_vector,
            query_filter=search_filter,
            limit=top_k,
            score_threshold=score_threshold,
            search_params=SearchParams(hnsw_ef=128, exact=False),
        )

        return [
            {
                "id": str(hit.id),
                "score": hit.score,
                "payload": hit.payload or {},
            }
            for hit in results
        ]
    except Exception as exc:
        logger.error("qdrant_search_error", error=str(exc))
        raise VectorDBError(f"Vector search failed: {exc}") from exc


async def delete_vector(article_id: str) -> None:
    """Delete a vector by article ID.

    Args:
        article_id: The point ID to delete.
    """
    settings = get_settings()
    client = get_qdrant_client()

    try:
        client.delete(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            points_selector=[article_id],
        )
        logger.debug("qdrant_vector_deleted", article_id=article_id)
    except Exception as exc:
        logger.error("qdrant_delete_error", article_id=article_id, error=str(exc))
        raise VectorDBError(f"Failed to delete vector: {exc}") from exc


def close_qdrant() -> None:
    """Close the Qdrant client and release the global reference."""
    global _client
    if _client is not None:
        _client.close()
        _client = None
        logger.info("qdrant_client_closed")
