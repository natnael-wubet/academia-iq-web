"""Ingest works from Crossref (authoritative DOI metadata).

Usage:
    python -m packages.ingestion.crossref_ingest "protein folding" --rows 100
"""

import argparse
import asyncio
import logging

from apps.api.core.db import SessionLocal
from apps.api.services.crossref import CrossrefClient
from packages.ingestion.store import upsert_work

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def ingest(query: str, rows: int = 100, from_year: int | None = None) -> int:
    filters = {"from-pub-date": f"{from_year}-01-01"} if from_year else None
    async with CrossrefClient() as client:
        items = await client.search_works(query, rows=rows, filters=filters)
        if not items:
            return 0
        with SessionLocal() as db:
            for raw in items:
                upsert_work(db, client.normalize_work(raw))
            db.commit()
        logger.info("Ingested %d Crossref works", len(items))
        return len(items)


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest works from Crossref")
    parser.add_argument("query")
    parser.add_argument("--rows", type=int, default=100)
    parser.add_argument("--from-year", type=int, default=None)
    args = parser.parse_args()
    total = asyncio.run(ingest(args.query, args.rows, args.from_year))
    logger.info("Done. %d works ingested.", total)


if __name__ == "__main__":
    main()
