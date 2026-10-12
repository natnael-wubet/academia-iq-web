from apps.api.schemas.common import SearchHit


def reciprocal_rank_fusion(
    ranked_lists: list[list[SearchHit]], k: int = 60, limit: int = 50
) -> list[SearchHit]:
    """Fuse multiple ranked result lists using Reciprocal Rank Fusion.

    score(d) = sum over lists of 1 / (k + rank(d))
    """
    scores: dict[int, float] = {}
    merged: dict[int, SearchHit] = {}

    for results in ranked_lists:
        for rank, hit in enumerate(results):
            scores[hit.id] = scores.get(hit.id, 0.0) + 1.0 / (k + rank + 1)
            existing = merged.get(hit.id)
            if existing is None:
                merged[hit.id] = hit
            else:
                if existing.abstract is None and hit.abstract is not None:
                    existing.abstract = hit.abstract
                existing.bm25_rank = existing.bm25_rank or hit.bm25_rank
                existing.vector_rank = existing.vector_rank or hit.vector_rank

    ordered = sorted(merged.values(), key=lambda h: scores[h.id], reverse=True)
    for hit in ordered:
        hit.score = scores[hit.id]
    return ordered[:limit]
