"""Entity resolution: match authors across OpenAlex, Semantic Scholar, and
ORCID using (1) exact ORCID iD, (2) normalized name + affiliation, and
(3) DOI overlap as a tie-breaker with confidence scoring.
"""

import logging
from dataclasses import dataclass

from rapidfuzz import fuzz
from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.api.models import Author, WorkAuthor
from packages.ingestion.store import normalize_name

logger = logging.getLogger(__name__)

NAME_THRESHOLD = 92
AFFILIATION_THRESHOLD = 85


@dataclass
class Match:
    kept_id: int
    merged_id: int
    confidence: float
    reason: str


def _affiliation(author: Author) -> str:
    return author.institution.name if author.institution else ""


def _doi_overlap(db: Session, a_id: int, b_id: int) -> int:
    a_works = {
        wa.work_id for wa in db.execute(
            select(WorkAuthor).where(WorkAuthor.author_id == a_id)
        ).scalars()
    }
    b_works = {
        wa.work_id for wa in db.execute(
            select(WorkAuthor).where(WorkAuthor.author_id == b_id)
        ).scalars()
    }
    return len(a_works & b_works)


def score_pair(db: Session, a: Author, b: Author) -> tuple[float, str]:
    if a.orcid and a.orcid == b.orcid:
        return 1.0, "orcid_exact"

    name_score = fuzz.token_sort_ratio(a.name_normalized, b.name_normalized) / 100.0
    if name_score < NAME_THRESHOLD / 100.0:
        return 0.0, "name_below_threshold"

    aff_score = 0.0
    aff_a, aff_b = _affiliation(a), _affiliation(b)
    if aff_a and aff_b:
        aff_score = fuzz.token_set_ratio(aff_a.lower(), aff_b.lower()) / 100.0

    overlap = _doi_overlap(db, a.id, b.id)
    overlap_score = min(overlap / 3.0, 1.0)

    confidence = 0.5 * name_score + 0.3 * aff_score + 0.2 * overlap_score
    reason = f"name={name_score:.2f} aff={aff_score:.2f} overlap={overlap}"
    return confidence, reason


def resolve_authors(db: Session, threshold: float = 0.75) -> list[Match]:
    """Find and merge duplicate author records. Returns the merged matches."""
    authors = db.execute(select(Author).order_by(Author.id)).scalars().all()
    merged_ids: set[int] = set()
    matches: list[Match] = []

    for i, a in enumerate(authors):
        if a.id in merged_ids:
            continue
        for b in authors[i + 1 :]:
            if b.id in merged_ids:
                continue
            confidence, reason = score_pair(db, a, b)
            if confidence >= threshold:
                _merge(db, keep=a, drop=b)
                merged_ids.add(b.id)
                matches.append(Match(a.id, b.id, confidence, reason))
                logger.info("Merged author %d into %d (%.2f, %s)", b.id, a.id, confidence, reason)

    db.commit()
    return matches


def _merge(db: Session, keep: Author, drop: Author) -> None:
    for field in ("openalex_id", "semantic_scholar_id", "orcid", "h_index"):
        if getattr(drop, field) and not getattr(keep, field):
            setattr(keep, field, getattr(drop, field))
    keep.works_count = max(keep.works_count, drop.works_count)
    keep.cited_by_count = max(keep.cited_by_count, drop.cited_by_count)

    links = db.execute(select(WorkAuthor).where(WorkAuthor.author_id == drop.id)).scalars().all()
    for link in links:
        existing = db.execute(
            select(WorkAuthor).where(
                WorkAuthor.work_id == link.work_id, WorkAuthor.author_id == keep.id
            )
        ).scalar_one_or_none()
        if existing:
            db.delete(link)
        else:
            link.author_id = keep.id
    db.delete(drop)


if __name__ == "__main__":
    from apps.api.core.db import SessionLocal

    logging.basicConfig(level=logging.INFO)
    with SessionLocal() as session:
        results = resolve_authors(session)
    print(f"Merged {len(results)} duplicate author records.")
