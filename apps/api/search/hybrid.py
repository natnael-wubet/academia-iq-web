import time

from sqlalchemy.orm import Session

from apps.api.core.config import get_settings
from apps.api.schemas.common import SearchHit
from apps.api.schemas.search import SearchRequest, SearchResponse
from apps.api.search.bm25 import bm25_search
from apps.api.search.fusion import reciprocal_rank_fusion
from apps.api.search.vector import vector_search
from apps.api.services.llm import summarize_results

settings = get_settings()


def _embed_query(query: str) -> list[float] | None:
    try:
        from packages.embeddings.embed import embed_texts

        return embed_texts([query])[0]
    except Exception:
        return None


def hybrid_search(db: Session, req: SearchRequest, rerank: bool | None = None) -> SearchResponse:
    start = time.perf_counter()
    candidate_limit = max(req.limit * 3, 50)

    bm25_hits: list[SearchHit] = []
    vector_hits: list[SearchHit] = []

    if req.mode in ("hybrid", "bm25"):
        bm25_hits = bm25_search(
            db,
            req.q,
            limit=candidate_limit,
            year_from=req.year_from,
            year_to=req.year_to,
            open_access_only=req.open_access_only,
        )

    if req.mode in ("hybrid", "vector"):
        query_vector = _embed_query(req.q)
        if query_vector:
            vector_hits = vector_search.search(
                query_vector,
                limit=candidate_limit,
                year_from=req.year_from,
                year_to=req.year_to,
            )

    if req.mode == "bm25":
        fused = bm25_hits
    elif req.mode == "vector":
        fused = vector_hits
    else:
        fused = reciprocal_rank_fusion([bm25_hits, vector_hits], limit=candidate_limit)

    fused = fused[req.offset : req.offset + req.limit]

    do_rerank = req.rerank if rerank is None else rerank
    summary = None
    if do_rerank and fused:
        ordered, summary = rerank_and_summarize(req.q, fused)
        fused = ordered

    took_ms = (time.perf_counter() - start) * 1000
    return SearchResponse(
        query=req.q,
        mode=req.mode,
        count=len(fused),
        took_ms=round(took_ms, 2),
        hits=fused,
        summary=summary,
    )


def rerank_and_summarize(query: str, hits: list[SearchHit]) -> tuple[list[SearchHit], str | None]:
    """LLM-based rerank using Groq; falls back to RRF order on any failure."""
    try:
        return summarize_results(query, hits)
    except Exception:
        return hits, None
