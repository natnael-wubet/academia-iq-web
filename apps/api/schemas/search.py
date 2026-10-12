from pydantic import BaseModel, Field

from apps.api.schemas.common import SearchHit


class SearchRequest(BaseModel):
    q: str = Field(min_length=1, max_length=512)
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    mode: str = Field(default="hybrid", pattern="^(hybrid|bm25|vector)$")
    year_from: int | None = None
    year_to: int | None = None
    open_access_only: bool = False
    rerank: bool = True


class SearchResponse(BaseModel):
    query: str
    mode: str
    count: int
    took_ms: float
    hits: list[SearchHit]
    summary: str | None = None
