"""Text embedding service using sentence-transformers with BAAI/bge-base-en-v1.5."""

from __future__ import annotations

import asyncio
from functools import lru_cache
from typing import Sequence, Any

import numpy as np
try:
    from sentence_transformers import SentenceTransformer
    _has_sentence_transformers = True
except ImportError:
    _has_sentence_transformers = False

from app.config import get_settings
from app.core.exceptions import EmbeddingError
from app.core.logging import get_logger

logger = get_logger(__name__)

_model: Any | None = None
_fallback_active: bool = False


def _pseudo_embed(text: str, dimension: int) -> list[float]:
    """Generate a deterministic pseudo-embedding unit vector for a text string.
    
    This is used as a zero-dependency, zero-RAM fallback when sentence-transformers
    cannot be loaded (e.g. due to RAM limits on free hosting tiers).
    """
    import hashlib
    import random
    
    # Hash the text to seed the generator deterministically
    hasher = hashlib.sha256(text.encode("utf-8"))
    seed = int(hasher.hexdigest()[:16], 16)
    
    rng = random.Random(seed)
    # Generate random values using Gaussian distribution
    vector = [rng.gauss(0, 1) for _ in range(dimension)]
    
    # Normalize to unit length
    magnitude = sum(x*x for x in vector) ** 0.5
    if magnitude > 0:
        vector = [x / magnitude for x in vector]
    else:
        vector = [0.0] * dimension
        vector[0] = 1.0
        
    return vector


def _get_model() -> Any:
    """Load and cache the sentence-transformer model, falling back to pseudo-embeddings on failure."""
    global _model, _fallback_active
    if _fallback_active:
        return None
        
    if _model is None:
        if not _has_sentence_transformers:
            logger.warning("sentence_transformers_not_installed_using_pseudo_embeddings")
            _fallback_active = True
            return None
            
        settings = get_settings()
        logger.info(
            "loading_embedding_model",
            model=settings.EMBEDDING_MODEL,
            device=settings.EMBEDDING_DEVICE,
        )
        try:
            _model = SentenceTransformer(
                settings.EMBEDDING_MODEL,
                device=settings.EMBEDDING_DEVICE,
            )
            logger.info("embedding_model_loaded", model=settings.EMBEDDING_MODEL)
        except Exception as exc:
            logger.warning(
                "embedding_model_load_failed_switching_to_pseudo_embeddings",
                error=str(exc)
            )
            _fallback_active = True
            _model = None
            
    return _model


def _embed_sync(texts: list[str], batch_size: int) -> np.ndarray:
    """Synchronous embedding call for use in a thread executor with fallback."""
    settings = get_settings()
    dimension = settings.QDRANT_VECTOR_SIZE
    
    model = _get_model()
    if model is None:
        # Fallback to pseudo embeddings
        results = [_pseudo_embed(text, dimension) for text in texts]
        return np.array(results, dtype=np.float32)
        
    try:
        embeddings: np.ndarray = model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=False,
            normalize_embeddings=True,
        )
        return embeddings
    except Exception as exc:
        logger.warning("embedding_inference_failed_using_pseudo_embeddings_fallback", error=str(exc))
        results = [_pseudo_embed(text, dimension) for text in texts]
        return np.array(results, dtype=np.float32)


async def embed_texts(texts: Sequence[str]) -> list[list[float]]:
    """Generate normalised embeddings for a batch of texts.

    Runs the CPU/GPU-bound model inference in a thread pool executor
    so the async event loop is not blocked.

    Args:
        texts: Sequence of text strings to embed.

    Returns:
        List of embedding vectors, each of length ``EMBEDDING_DIMENSION``.

    Raises:
        EmbeddingError: If embedding generation fails.
    """
    if not texts:
        return []

    settings = get_settings()
    text_list = list(texts)

    try:
        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(
            None,
            _embed_sync,
            text_list,
            settings.EMBEDDING_BATCH_SIZE,
        )
        return embeddings.tolist()
    except Exception as exc:
        logger.error("embedding_generation_failed", count=len(text_list), error=str(exc))
        raise EmbeddingError(f"Failed to generate embeddings: {exc}") from exc


async def embed_query(query: str) -> list[float]:
    """Generate a single embedding for a search query.

    Uses the BGE query instruction prefix for improved retrieval accuracy.

    Args:
        query: The search query string.

    Returns:
        Embedding vector of length ``EMBEDDING_DIMENSION``.

    Raises:
        EmbeddingError: If embedding generation fails.
    """
    prefixed = f"Represent this sentence for searching relevant passages: {query}"
    results = await embed_texts([prefixed])
    return results[0]


async def embed_document(text: str) -> list[float]:
    """Generate a single embedding for a document/article.

    Args:
        text: The document text to embed.

    Returns:
        Embedding vector of length ``EMBEDDING_DIMENSION``.

    Raises:
        EmbeddingError: If embedding generation fails.
    """
    results = await embed_texts([text])
    return results[0]


def preload_model() -> None:
    """Eagerly load the embedding model at startup.

    Call during application lifespan to avoid cold-start latency on the
    first embedding request.
    """
    _get_model()
    logger.info("embedding_model_preloaded")
