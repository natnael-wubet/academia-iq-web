from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from apps.api.core.db import get_db
from apps.api.schemas.search import SearchRequest, SearchResponse
from apps.api.search.hybrid import hybrid_search

router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=SearchResponse)
def search(
    q: str = Query(..., min_length=1, max_length=512),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    mode: str = Query("hybrid", pattern="^(hybrid|bm25|vector)$"),
    year_from: int | None = None,
    year_to: int | None = None,
    open_access_only: bool = False,
    rerank: bool = True,
    db: Session = Depends(get_db),
) -> SearchResponse:
    req = SearchRequest(
        q=q,
        limit=limit,
        offset=offset,
        mode=mode,
        year_from=year_from,
        year_to=year_to,
        open_access_only=open_access_only,
        rerank=rerank,
    )
    return hybrid_search(db, req)
