import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from apps.api.core.config import get_settings
from apps.api.core.db import Base, engine
from apps.api.routers import authors, health, institutions, search, trends

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
    # For local development; production uses Alembic migrations.
    if settings.environment == "development":
        Base.metadata.create_all(bind=engine)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logging.exception("Unhandled error on %s", request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


for router in (health.router, search.router, authors.router, institutions.router, trends.router):
    app.include_router(router, prefix=settings.api_v1_prefix)


@app.get("/")
def root() -> dict:
    return {"name": settings.app_name, "docs": "/docs", "api": settings.api_v1_prefix}
