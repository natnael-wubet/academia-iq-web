from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from apps.api.core.cache import cache
from apps.api.core.db import get_db

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.get("/ready")
def ready(db: Session = Depends(get_db)) -> dict:
    db_ok = True
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_ok = False
    return {
        "database": db_ok,
        "cache": cache.client is not None,
    }
