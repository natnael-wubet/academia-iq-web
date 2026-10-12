#!/bin/sh
set -e

if [ -n "$DATABASE_URL" ]; then
    echo "Running database migrations..."
    alembic upgrade head || echo "WARNING: alembic upgrade failed; continuing startup"
else
    echo "DATABASE_URL not set; skipping migrations"
fi

exec uvicorn apps.api.main:app --host 0.0.0.0 --port "${PORT:-8000}"
