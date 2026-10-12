"""Persistence helpers shared by all ingestion pipelines."""

import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.api.models import Author, Citation, Institution, Venue, Work, WorkAuthor


def normalize_name(name: str) -> str:
    import unicodedata

    name = unicodedata.normalize("NFD", name)
    name = "".join(c for c in name if not unicodedata.combining(c))
    name = re.sub(r"[^\w\s]", " ", name.lower())
    return re.sub(r"\s+", " ", name).strip()


def get_or_create_venue(db: Session, data: dict | None) -> Venue | None:
    if not data or not data.get("name"):
        return None
    venue = None
    if data.get("openalex_id"):
        venue = db.execute(
            select(Venue).where(Venue.openalex_id == data["openalex_id"])
        ).scalar_one_or_none()
    if venue is None and data.get("issn_l"):
        venue = db.execute(
            select(Venue).where(Venue.issn_l == data["issn_l"])
        ).scalar_one_or_none()
    if venue is None:
        venue = Venue(
            openalex_id=data.get("openalex_id"),
            issn_l=data.get("issn_l"),
            name=data["name"],
            type=data.get("type"),
        )
        db.add(venue)
        db.flush()
    return venue


def get_or_create_institution(db: Session, data: dict) -> Institution | None:
    if not data or not data.get("name"):
        return None
    inst = None
    if data.get("openalex_id"):
        inst = db.execute(
            select(Institution).where(Institution.openalex_id == data["openalex_id"])
        ).scalar_one_or_none()
    if inst is None and data.get("ror_id"):
        inst = db.execute(
            select(Institution).where(Institution.ror_id == data["ror_id"])
        ).scalar_one_or_none()
    if inst is None:
        inst = Institution(
            openalex_id=data.get("openalex_id"),
            ror_id=data.get("ror_id"),
            name=data["name"],
            country_code=data.get("country_code"),
            type=data.get("type"),
        )
        db.add(inst)
        db.flush()
    return inst


def get_or_create_author(db: Session, data: dict) -> Author | None:
    if not data or not data.get("display_name"):
        return None
    author = None
    for field in ("openalex_id", "semantic_scholar_id", "orcid"):
        value = data.get(field)
        if value:
            author = db.execute(
                select(Author).where(getattr(Author, field) == value)
            ).scalar_one_or_none()
            if author:
                break
    if author is None:
        author = Author(
            openalex_id=data.get("openalex_id"),
            semantic_scholar_id=data.get("semantic_scholar_id"),
            orcid=data.get("orcid"),
            display_name=data["display_name"],
            name_normalized=normalize_name(data["display_name"]),
        )
        db.add(author)
        db.flush()
    else:
        # Enrich missing identifiers.
        for field in ("openalex_id", "semantic_scholar_id", "orcid"):
            if data.get(field) and not getattr(author, field):
                setattr(author, field, data[field])
    return author


def upsert_work(db: Session, data: dict) -> Work:
    work = None
    if data.get("doi"):
        work = db.execute(select(Work).where(Work.doi == data["doi"])).scalar_one_or_none()
    if work is None and data.get("openalex_id"):
        work = db.execute(
            select(Work).where(Work.openalex_id == data["openalex_id"])
        ).scalar_one_or_none()
    if work is None and data.get("semantic_scholar_id"):
        work = db.execute(
            select(Work).where(Work.semantic_scholar_id == data["semantic_scholar_id"])
        ).scalar_one_or_none()

    if work is None:
        work = Work()
        db.add(work)

    for field in (
        "openalex_id", "doi", "semantic_scholar_id", "title", "abstract",
        "publication_date", "publication_year", "cited_by_count",
        "reference_count", "type", "language", "is_open_access", "source",
    ):
        if data.get(field) is not None:
            setattr(work, field, data[field])

    venue = get_or_create_venue(db, data.get("venue"))
    if venue:
        work.venue = venue

    db.flush()
    _refresh_search_vector(db, work)

    for position, author_data in enumerate(data.get("authors") or []):
        author = get_or_create_author(db, author_data)
        if author is None:
            continue
        exists = db.execute(
            select(WorkAuthor).where(
                WorkAuthor.work_id == work.id, WorkAuthor.author_id == author.id
            )
        ).scalar_one_or_none()
        if not exists:
            db.add(
                WorkAuthor(
                    work_id=work.id,
                    author_id=author.id,
                    position=position,
                    author_position=author_data.get("position"),
                )
            )
        for inst_data in author_data.get("institutions") or []:
            inst = get_or_create_institution(db, inst_data)
            if inst and not author.last_known_institution_id:
                author.last_known_institution_id = inst.id
    db.flush()
    return work


def _refresh_search_vector(db: Session, work: Work) -> None:
    from sqlalchemy import text

    db.execute(
        text(
            """
            UPDATE works
            SET search_vector =
                setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
                setweight(to_tsvector('english', coalesce(abstract, '')), 'B')
            WHERE id = :id
            """
        ),
        {"id": work.id},
    )


def link_citations(db: Session, citing: Work, referenced_dois: list[str]) -> int:
    linked = 0
    for doi in referenced_dois:
        doi = doi.lower()
        cited = db.execute(select(Work).where(Work.doi == doi)).scalar_one_or_none()
        if cited is None or cited.id == citing.id:
            continue
        exists = db.execute(
            select(Citation).where(
                Citation.citing_work_id == citing.id,
                Citation.cited_work_id == cited.id,
            )
        ).scalar_one_or_none()
        if not exists:
            db.add(Citation(citing_work_id=citing.id, cited_work_id=cited.id))
            linked += 1
    return linked
