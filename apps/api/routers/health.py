from fastapi import APIRouter, Depends
from sqlalchemy import inspect, text
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


@router.get("/health/db")
def health_db(db: Session = Depends(get_db)) -> dict:
    """Diagnostics: connection, applied migration, and visible tables."""
    info: dict = {
        "connected": False,
        "tables": [],
        "alembic_revision": None,
        "error": None,
    }
    try:
        info["tables"] = sorted(inspect(db.get_bind()).get_table_names())
        info["connected"] = True
        try:
            info["alembic_revision"] = db.execute(
                text("SELECT version_num FROM alembic_version")
            ).scalar()
        except Exception as exc:  # table missing == migrations never ran
            info["error"] = f"alembic_version: {type(exc).__name__}: {exc}"
    except Exception as exc:
        info["error"] = f"{type(exc).__name__}: {exc}"
    return info
