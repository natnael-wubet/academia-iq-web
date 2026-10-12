from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    total: int
    limit: int
    offset: int
    items: list[T]


class SearchHit(BaseModel):
    id: int
    title: str
    abstract: str | None = None
    publication_year: int | None = None
    cited_by_count: int = 0
    doi: str | None = None
    score: float = 0.0
    source: str | None = None
    bm25_rank: int | None = None
    vector_rank: int | None = None
