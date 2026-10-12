"""Embedding generation with sentence-transformers, plus a deterministic
hash-based fallback so the pipeline works with zero model downloads.
"""

import hashlib
import logging
import math

from apps.api.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_model = None


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer(settings.embedding_model)
    return _model


def _hash_embed(text: str) -> list[float]:
    """Deterministic bag-of-words hashing embedding (fallback, no downloads)."""
    dim = settings.embedding_dim
    vec = [0.0] * dim
    for token in text.lower().split():
        h = int(hashlib.md5(token.encode()).hexdigest(), 16)
        vec[h % dim] += 1.0
    return normalize(vec)


def normalize(vec: list[float]) -> list[float]:
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    if not settings.use_local_embeddings:
        # Fast, dependency-free, deterministic. Avoids a request-time model
        # download; set USE_LOCAL_EMBEDDINGS=true to enable the real model.
        return [_hash_embed(t) for t in texts]
    try:
        model = _get_model()
        vectors = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        return [list(map(float, v)) for v in vectors]
    except Exception as exc:  # pragma: no cover - depends on model availability
        logger.warning("sentence-transformers unavailable, using hash embedding: %s", exc)
        return [_hash_embed(t) for t in texts]


def work_text(title: str, abstract: str | None) -> str:
    return f"{title}\n\n{abstract or ''}".strip()
