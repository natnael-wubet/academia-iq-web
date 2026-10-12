"""Ingest works from OpenAlex into the local database.

Usage:
    python -m packages.ingestion.openalex_ingest "quantum computing" --pages 5
"""

import argparse
import asyncio
import logging

from sqlalchemy.orm import Session

from apps.api.core.db import SessionLocal
from apps.api.services.openalex import OpenAlexClient
from packages.ingestion.store import link_citations, upsert_work

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def ingest(query: str, pages: int = 1, per_page: int = 50) -> int:
    total = 0
    async with OpenAlexClient() as client:
        for page in range(1, pages + 1):
            raw_works = await client.search_works(query, per_page=per_page, page=page)
            if not raw_works:
                break
            with SessionLocal() as db:
                total += _persist(db, client, raw_works)
            logger.info("Page %d: %d works ingested (total %d)", page, len(raw_works), total)
    return total


def _persist(db: Session, client: OpenAlexClient, raw_works: list[dict]) -> int:
    count = 0
    for raw in raw_works:
        normalized = client.normalize_work(raw)
        work = upsert_work(db, normalized)
        refs = [
            r.replace("https://doi.org/", "").lower()
            for r in normalized.get("referenced_works", [])
            if r.startswith("https://doi.org/")
        ]
        link_citations(db, work, refs)
        count += 1
    db.commit()
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest works from OpenAlex")
    parser.add_argument("query")
    parser.add_argument("--pages", type=int, default=1)
    parser.add_argument("--per-page", type=int, default=50)
    args = parser.parse_args()
    total = asyncio.run(ingest(args.query, args.pages, args.per_page))
    logger.info("Done. %d works ingested.", total)


if __name__ == "__main__":
    main()
