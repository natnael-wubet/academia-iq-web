from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from apps.api.core.db import get_db
from apps.api.models import Institution, Work, WorkInstitution
from apps.api.schemas.common import Page
from apps.api.schemas.entities import InstitutionOut

router = APIRouter(prefix="/institutions", tags=["institutions"])


@router.get("", response_model=Page[InstitutionOut])
def list_institutions(
    q: str | None = None,
    country: str | None = None,
    limit: int = Query(25, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> Page[InstitutionOut]:
    stmt = select(Institution)
    count_stmt = select(func.count(Institution.id))
    if q:
        pattern = f"%{q.lower()}%"
        stmt = stmt.where(func.lower(Institution.name).like(pattern))
        count_stmt = count_stmt.where(func.lower(Institution.name).like(pattern))
    if country:
        stmt = stmt.where(Institution.country_code == country.upper())
        count_stmt = count_stmt.where(Institution.country_code == country.upper())
    total = db.execute(count_stmt).scalar_one()
    stmt = stmt.order_by(Institution.cited_by_count.desc()).limit(limit).offset(offset)
    items = db.execute(stmt).scalars().all()
    return Page(total=total, limit=limit, offset=offset, items=list(items))


@router.get("/{institution_id}", response_model=InstitutionOut)
def get_institution(institution_id: int, db: Session = Depends(get_db)) -> Institution:
    inst = db.get(Institution, institution_id)
    if inst is None:
        raise HTTPException(status_code=404, detail="Institution not found")
    return inst


@router.get("/{institution_id}/stats")
def institution_stats(institution_id: int, db: Session = Depends(get_db)) -> dict:
    """Institutional benchmarking: output by year and top venues."""
    works_by_year = dict(
        db.execute(
            select(Work.publication_year, func.count(Work.id))
            .join(WorkInstitution, WorkInstitution.work_id == Work.id)
            .where(WorkInstitution.institution_id == institution_id)
            .group_by(Work.publication_year)
        ).all()
    )
    top_venues = dict(
        db.execute(
            select(Work.venue_id, func.count(Work.id))
            .join(WorkInstitution, WorkInstitution.work_id == Work.id)
            .where(WorkInstitution.institution_id == institution_id)
            .group_by(Work.venue_id)
            .order_by(func.count(Work.id).desc())
            .limit(5)
        ).all()
    )
    return {"works_by_year": works_by_year, "top_venue_ids": top_venues}
