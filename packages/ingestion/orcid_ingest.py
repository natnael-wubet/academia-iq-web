"""Enrich author profiles from ORCID (verified researcher identity).

Usage:
    python -m packages.ingestion.orcid_ingest "Jane Doe"
"""

import argparse
import asyncio
import logging

from sqlalchemy import select

from apps.api.core.db import SessionLocal
from apps.api.models import Author
from apps.api.services.orcid import OrcidClient
from packages.ingestion.store import normalize_name

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def enrich(name: str, rows: int = 25) -> int:
    updated = 0
    async with OrcidClient() as client:
        orcids = await client.search(f'given-and-family-names:"{name}"', rows=rows)
        for orcid_id in orcids:
            record = await client.fetch_record(orcid_id)
            profile = client.normalize_profile(orcid_id, record)
            employments = await client.fetch_employments(orcid_id)
            with SessionLocal() as db:
                author = db.execute(
                    select(Author).where(Author.orcid == orcid_id)
                ).scalar_one_or_none()
                if author is None:
                    normalized = normalize_name(profile["display_name"])
                    author = db.execute(
                        select(Author).where(Author.name_normalized == normalized)
                    ).scalar_one_or_none()
                if author is None:
                    author = Author(
                        orcid=orcid_id,
                        display_name=profile["display_name"],
                        name_normalized=normalize_name(profile["display_name"]),
                    )
                    db.add(author)
                author.orcid = orcid_id
                if employments:
                    org = (employments[0].get("organization") or {}).get("name")
                    if org:
                        logger.info("Author %s -> %s", author.display_name, org)
                db.commit()
                updated += 1
    return updated


def main() -> None:
    parser = argparse.ArgumentParser(description="Enrich authors from ORCID")
    parser.add_argument("name")
    parser.add_argument("--rows", type=int, default=25)
    args = parser.parse_args()
    total = asyncio.run(enrich(args.name, args.rows))
    logger.info("Done. %d ORCID profiles processed.", total)


if __name__ == "__main__":
    main()
