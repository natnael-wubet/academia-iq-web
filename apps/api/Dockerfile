# --- Stage 1: build the Next.js static frontend ---------------------------
FROM node:20-slim AS web
WORKDIR /web
COPY apps/web/package.json ./
RUN npm install
COPY apps/web ./
RUN npm run build

# --- Stage 2: Python API + serve the built frontend -----------------------
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONPATH=/app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY apps ./apps
COPY packages ./packages
COPY alembic ./alembic
COPY alembic.ini ./alembic.ini

# Overlay the compiled static site so the API can serve it at /web.
COPY --from=web /web/out ./apps/web/out

RUN chmod +x apps/api/entrypoint.sh

EXPOSE 8000

CMD ["sh", "apps/api/entrypoint.sh"]
