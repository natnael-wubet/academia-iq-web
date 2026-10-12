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

RUN chmod +x apps/api/entrypoint.sh

EXPOSE 8000

CMD ["sh", "apps/api/entrypoint.sh"]
