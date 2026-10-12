"""Ingest papers and embeddings from Semantic Scholar.

Usage:
    python -m packages.ingestion.semscholar_ingest "graph neural networks" --limit 100
"""

import argparse
import asyncio
import logging

from apps.api.core.db import SessionLocal
from apps.api.models import Embedding
from apps.api.services.semantic_scholar import SemanticScholarClient
from packages.ingestion.store import upsert_work

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def ingest(query: str, limit: int = 100, with_embeddings: bool = True) -> int:
    total = 0
    async with SemanticScholarClient() as client:
        offset = 0
        while offset < limit:
            batch = min(100, limit - offset)
            papers = await client.search_papers(query, limit=batch, offset=offset)
            if not papers:
                break
            with SessionLocal() as db:
                for raw in papers:
                    normalized = client.normalize_paper(raw)
                    embedding = normalized.pop("embedding", None)
                    work = upsert_work(db, normalized)
                    if with_embeddings and embedding:
                        _store_embedding(db, work.id, embedding)
                    total += 1
                db.commit()
            offset += batch
            logger.info("Ingested %d papers so far", total)
    return total


def _store_embedding(db, work_id: int, vector: list[float]) -> None:
    if db.get(Embedding, work_id):
        return
    db.add(
        Embedding(
            work_id=work_id,
            model="specter2",
            dim=len(vector),
            vector=list(map(float, vector)),
            norm=1.0,
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest papers from Semantic Scholar")
    parser.add_argument("query")
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--no-embeddings", action="store_true")
    args = parser.parse_args()
    total = asyncio.run(ingest(args.query, args.limit, not args.no_embeddings))
    logger.info("Done. %d papers ingested.", total)


if __name__ == "__main__":
    main()
