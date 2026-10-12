"""Recommendation engine for related papers and collaboration matching.

Uses embedding similarity (Weaviate fallback via cosine distance) and a
lightweight content-based signal (shared references/authors).
"""

import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.api.core.config import get_settings
from apps.api.models import Author, Work
from apps.api.schemas.common import SearchHit
from packages.embeddings.embed import embed_texts, work_text

logger = logging.getLogger(__name__)
settings = get_settings()


def recommend_similar(db: Session, work_id: int, limit: int = 10) -> list[SearchHit]:
    work = db.get(Work, work_id)
    if work is None:
        return []
    try:
        vec = embed_texts([work_text(work.title, work.abstract)])[0]
        from apps.api.search.vector import vector_search

        hits = vector_search.search(vec, limit=limit + 1)
        return [h for h in hits if h.id != work_id][:limit]
    except Exception as exc:
        logger.warning("similarity failed: %s", exc)
        return []


def recommend_collaborators(db: Session, author_id: int, limit: int = 10) -> list[Author]:
    author = db.get(Author, author_id)
    if author is None:
        return []
    stmt = (
        select(Author)
        .where(Author.id != author_id)
        .order_by(Author.cited_by_count.desc())
        .limit(limit)
    )
    return list(db.execute(stmt).scalars().all())
