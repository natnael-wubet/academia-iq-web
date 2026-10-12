# Academia IQ

A research intelligence platform built on four free APIs — **OpenAlex**,
**Semantic Scholar**, **Crossref**, and **ORCID** — with fully free-tier
infrastructure (PostgreSQL, Redis, Weaviate, Cloudflare, Vercel, Groq).

See [`all.md`](./all.md) for the complete build & launch blueprint.

## Architecture

```
apps/
  api/        FastAPI backend (search, authors, institutions, trends)
  web/        Next.js frontend
  workers/    Cloudflare Workers API gateway
packages/
  ingestion/  Data ingestion pipelines (OpenAlex, S2, Crossref, ORCID)
  embeddings/ Embedding generation
  ml/         Recommendation & citation prediction models
```

## Quick start (local)

```bash
docker compose up -d postgres redis
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn apps.api.main:app --reload
```

The API docs are then available at http://localhost:8000/docs.

## Search architecture

Hybrid retrieval combines PostgreSQL `tsvector` BM25 ranking with vector
similarity, fused by reciprocal rank fusion (RRF), then reranked by an LLM.

```
Query ──┬─▶ BM25 (Postgres)   ──┐
        └─▶ Vector (Weaviate) ──┴─▶ RRF ─▶ LLM rerank ─▶ Results
```

## License

MIT. All upstream data is attributed to its source and used under its
respective license.
