#!/bin/sh
set -e

if [ -n "$DATABASE_URL" ]; then
    echo "Running database migrations..."
    attempt=0
    until alembic upgrade head; do
        attempt=$((attempt + 1))
        if [ "$attempt" -ge 5 ]; then
            echo "ERROR: alembic upgrade failed after $attempt attempts." >&2
            echo "       The API will start WITHOUT a migrated schema." >&2
            echo "       Inspect GET /api/v1/health/db for details." >&2
            break
        fi
        echo "Migration attempt $attempt failed; retrying in 3s..." >&2
        sleep 3
    done
else
    echo "DATABASE_URL not set; skipping migrations" >&2
fi

exec uvicorn apps.api.main:app --host 0.0.0.0 --port "${PORT:-8000}"
