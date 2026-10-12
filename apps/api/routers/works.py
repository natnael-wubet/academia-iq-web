from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from apps.api.core.db import get_db
from apps.api.models import Citation, Work
from apps.api.schemas.common import Page
from apps.api.schemas.entities import WorkOut

router = APIRouter(prefix="/works", tags=["works"])


@router.get("", response_model=Page[WorkOut])
def list_works(
    year: int | None = None,
    limit: int = Query(25, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> Page[WorkOut]:
    stmt = select(Work).options(selectinload(Work.authors), selectinload(Work.venue))
    count_stmt = select(func.count(Work.id))
    if year is not None:
        stmt = stmt.where(Work.publication_year == year)
        count_stmt = count_stmt.where(Work.publication_year == year)
    total = db.execute(count_stmt).scalar_one()
    stmt = stmt.order_by(Work.cited_by_count.desc()).limit(limit).offset(offset)
    works = db.execute(stmt).scalars().all()
    return Page(total=total, limit=limit, offset=offset, items=list(works))


@router.get("/{work_id}", response_model=WorkOut)
def get_work(work_id: int, db: Session = Depends(get_db)) -> Work:
    work = db.execute(
        select(Work)
        .options(selectinload(Work.authors), selectinload(Work.venue))
        .where(Work.id == work_id)
    ).scalar_one_or_none()
    if work is None:
        raise HTTPException(status_code=404, detail="Work not found")
    return work


@router.get("/{work_id}/references", response_model=Page[WorkOut])
def get_references(
    work_id: int,
    limit: int = Query(25, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> Page[WorkOut]:
    stmt = (
        select(Work)
        .join(Citation, Citation.cited_work_id == Work.id)
        .where(Citation.citing_work_id == work_id)
        .options(selectinload(Work.authors), selectinload(Work.venue))
    )
    total = db.execute(
        select(func.count()).select_from(
            select(Citation).where(Citation.citing_work_id == work_id).subquery()
        )
    ).scalar_one()
    works = db.execute(stmt.limit(limit).offset(offset)).scalars().all()
    return Page(total=total, limit=limit, offset=offset, items=list(works))


@router.get("/{work_id}/cited-by", response_model=Page[WorkOut])
def get_cited_by(
    work_id: int,
    limit: int = Query(25, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> Page[WorkOut]:
    stmt = (
        select(Work)
        .join(Citation, Citation.citing_work_id == Work.id)
        .where(Citation.cited_work_id == work_id)
        .options(selectinload(Work.authors), selectinload(Work.venue))
        .order_by(Work.cited_by_count.desc())
        .limit(limit)
        .offset(offset)
    )
    total = (
        db.execute(
            select(func.count(Citation.citing_work_id)).where(Citation.cited_work_id == work_id)
        ).scalar_one()
        or 0
    )
    works = db.execute(stmt).scalars().all()
    return Page(total=total, limit=limit, offset=offset, items=list(works))
