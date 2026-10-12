from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from apps.api.core.db import get_db
from apps.api.models import Author, Work
from apps.api.models.link import WorkAuthor
from apps.api.schemas.common import Page
from apps.api.schemas.entities import AuthorOut, WorkOut

router = APIRouter(prefix="/authors", tags=["authors"])


@router.get("", response_model=Page[AuthorOut])
def list_authors(
    q: str | None = None,
    limit: int = Query(25, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> Page[AuthorOut]:
    stmt = select(Author).options(selectinload(Author.institution))
    count_stmt = select(func.count(Author.id))
    if q:
        pattern = f"%{q.lower()}%"
        stmt = stmt.where(Author.name_normalized.like(pattern))
        count_stmt = count_stmt.where(Author.name_normalized.like(pattern))
    total = db.execute(count_stmt).scalar_one()
    stmt = stmt.order_by(Author.cited_by_count.desc()).limit(limit).offset(offset)
    authors = db.execute(stmt).scalars().all()
    return Page(total=total, limit=limit, offset=offset, items=list(authors))


@router.get("/{author_id}", response_model=AuthorOut)
def get_author(author_id: int, db: Session = Depends(get_db)) -> Author:
    author = db.execute(
        select(Author).options(selectinload(Author.institution)).where(Author.id == author_id)
    ).scalar_one_or_none()
    if author is None:
        raise HTTPException(status_code=404, detail="Author not found")
    return author


@router.get("/{author_id}/works", response_model=list[WorkOut])
def get_author_works(
    author_id: int,
    limit: int = Query(25, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[Work]:
    stmt = (
        select(Work)
        .join(WorkAuthor, WorkAuthor.work_id == Work.id)
        .where(WorkAuthor.author_id == author_id)
        .order_by(Work.cited_by_count.desc())
        .limit(limit)
    )
    return list(db.execute(stmt).scalars().all())
