from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from apps.api.models import Work
from apps.api.schemas.common import SearchHit


def bm25_search(
    db: Session,
    query: str,
    limit: int = 50,
    year_from: int | None = None,
    year_to: int | None = None,
    open_access_only: bool = False,
) -> list[SearchHit]:
    """Full-text search over works using PostgreSQL tsvector + ts_rank_cd.

    Ranks against the precomputed `search_vector` column indexed with GIN.
    """
    tsquery = func.websearch_to_tsquery("english", query)
    rank = func.ts_rank_cd(Work.search_vector, tsquery)

    stmt = (
        select(Work, rank.label("rank"))
        .where(Work.search_vector.op("@@")(tsquery))
        .order_by(rank.desc(), Work.cited_by_count.desc())
        .limit(limit)
    )
    if year_from is not None:
        stmt = stmt.where(Work.publication_year >= year_from)
    if year_to is not None:
        stmt = stmt.where(Work.publication_year <= year_to)
    if open_access_only:
        stmt = stmt.where(Work.is_open_access.is_(True))

    rows = db.execute(stmt).all()
    return [
        SearchHit(
            id=work.id,
            title=work.title,
            abstract=work.abstract,
            publication_year=work.publication_year,
            cited_by_count=work.cited_by_count,
            doi=work.doi,
            score=float(rank_value),
            source=work.source,
            bm25_rank=i,
        )
        for i, (work, rank_value) in enumerate(rows)
    ]
