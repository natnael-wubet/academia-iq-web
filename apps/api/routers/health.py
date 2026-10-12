import os

from fastapi import APIRouter, Depends
from sqlalchemy import inspect, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from apps.api.core.cache import cache
from apps.api.core.config import get_settings
from apps.api.core.db import get_db

router = APIRouter(tags=["health"])


def _safe_host(url: str) -> str | None:
    try:
        parsed = make_url(url)
    except Exception:
        return None
    host = parsed.host or ""
    if parsed.port:
        host = f"{host}:{parsed.port}"
    return f"{parsed.drivername}://{host}/{parsed.database or ''}"


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
    settings = get_settings()
    env_names = [
        "DATABASE_URL",
        "DATABASE_INTERNAL_URL",
        "DATABASE_URL_INTERNAL",
        "POSTGRES_URL",
        "POSTGRESQL_URL",
    ]
    info: dict = {
        "connected": False,
        "tables": [],
        "alembic_revision": None,
        "error": None,
        "env": {
            "present": {name: bool(os.environ.get(name)) for name in env_names},
            "resolved_url": _safe_host(settings.database_url),
            "environment": settings.environment,
            "render_service": os.environ.get("RENDER_SERVICE_NAME"),
            "render_region": os.environ.get("RENDER_REGION"),
            "render_commit": os.environ.get("RENDER_GIT_COMMIT"),
        },
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
