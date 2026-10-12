"""Batch-embed works and upsert vectors into Weaviate + the local mirror."""

import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.api.core.config import get_settings
from apps.api.models import Embedding, Work
from packages.embeddings.embed import embed_texts, work_text

logger = logging.getLogger(__name__)
settings = get_settings()


def embed_works(db: Session, batch_size: int = 256, limit: int | None = None) -> int:
    stmt = (
        select(Work)
        .outerjoin(Embedding, Embedding.work_id == Work.id)
        .where(Embedding.work_id.is_(None))
        .order_by(Work.cited_by_count.desc())
    )
    if limit:
        stmt = stmt.limit(limit)

    works = db.execute(stmt).scalars().all()
    total = 0
    for i in range(0, len(works), batch_size):
        batch = works[i : i + batch_size]
        vectors = embed_texts([work_text(w.title, w.abstract) for w in batch])
        for work, vec in zip(batch, vectors):
            db.add(
                Embedding(
                    work_id=work.id,
                    model=settings.embedding_model,
                    dim=len(vec),
                    vector=vec,
                    norm=1.0,
                )
            )
            total += 1
        db.commit()
        logger.info("Embedded %d/%d works", total, len(works))
    return total
