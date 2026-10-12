import logging
import os
from pathlib import Path

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from apps.api.core.config import get_settings
from apps.api.core.db import Base, engine
from apps.api.routers import authors, health, institutions, search, trends, works

logging.basicConfig(level=logging.INFO)
settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Free research intelligence over OpenAlex, Semantic Scholar, Crossref, and ORCID.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    from sqlalchemy import inspect, text

    # For local development only; production uses Alembic migrations.
    # Never let an unreachable database prevent the API (health checks,
    # OpenAPI docs) from starting.
    if settings.environment == "development":
        try:
            Base.metadata.create_all(bind=engine)
        except Exception as exc:  # pragma: no cover - depends on env
            logging.warning("Skipping create_all (database unavailable): %s", exc)

    # Log database connectivity up-front so misconfiguration is obvious in the
    # Render logs instead of surfacing as a generic 500 on the first query.
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            tables = sorted(inspect(conn).get_table_names())
        logging.info("Database OK (%d tables): %s", len(tables), ", ".join(tables[:12]))
    except Exception as exc:
        logging.error("Database not reachable or unmigrated: %s", exc)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logging.exception("Unhandled error on %s", request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


for router in (
    health.router,
    search.router,
    authors.router,
    institutions.router,
    trends.router,
    works.router,
):
    app.include_router(router, prefix=settings.api_v1_prefix)


@app.get("/")
def root() -> dict:
    return {
        "name": settings.app_name,
        "docs": "/docs",
        "api": settings.api_v1_prefix,
        "web": "/web",
    }


@app.get("/favicon.ico", include_in_schema=False)
def favicon() -> Response:
    # The browser requests the site root; the UI lives under /web.
    return Response(status_code=204)


# --- Static frontend -------------------------------------------------------
# The Next.js app is exported to `apps/web/out` (basePath `/web`) and served
# from the same container as the API so that a single Render service hosts
# both. Unknown paths under `/web` fall back to the exported index.html so the
# client-side router can render detail pages.
WEB_ROOT = Path(
    os.environ.get("WEB_ROOT", Path(__file__).resolve().parents[1] / "web" / "out")
)


def _safe_web_file(relative: str) -> Path | None:
    candidate = (WEB_ROOT / relative).resolve()
    try:
        candidate.relative_to(WEB_ROOT.resolve())
    except ValueError:
        return None
    if candidate.is_file():
        return candidate
    if candidate.is_dir() and (candidate / "index.html").is_file():
        return candidate / "index.html"
    return None


if (WEB_ROOT / "index.html").is_file():
    logging.info("Serving web frontend from %s", WEB_ROOT)

    @app.get("/web", include_in_schema=False)
    @app.get("/web/{full_path:path}", include_in_schema=False)
    def web_app(full_path: str = "") -> FileResponse:
        resolved = _safe_web_file(full_path) if full_path else None
        if resolved is None:
            # SPA fallback for client-side detail routes.
            resolved = WEB_ROOT / "index.html"
        return FileResponse(resolved)
