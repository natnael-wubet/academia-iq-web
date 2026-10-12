import json
import logging

import httpx

from apps.api.core.config import get_settings
from apps.api.schemas.common import SearchHit

logger = logging.getLogger(__name__)
settings = get_settings()

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


def _chat(messages: list[dict], temperature: float = 0.2, max_tokens: int = 512) -> str:
    if not settings.groq_api_key:
        raise RuntimeError("GROQ_API_KEY not configured")
    resp = httpx.post(
        GROQ_URL,
        headers={"Authorization": f"Bearer {settings.groq_api_key}"},
        json={
            "model": settings.groq_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        },
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


def summarize_paper(title: str, abstract: str | None) -> str:
    return _chat(
        [
            {"role": "system", "content": "Summarize academic papers in 2 concise sentences."},
            {"role": "user", "content": f"Title: {title}\n\nAbstract: {abstract or 'N/A'}"},
        ]
    )


def summarize_field(topic: str, titles: list[str]) -> str:
    joined = "\n".join(f"- {t}" for t in titles[:25])
    return _chat(
        [
            {"role": "system", "content": "You are a research analyst. Summarize a field briefly."},
            {"role": "user", "content": f"Topic: {topic}\nRecent papers:\n{joined}"},
        ],
        max_tokens=768,
    )


def rerank(query: str, hits: list[SearchHit], top_n: int = 20) -> list[int]:
    listing = "\n".join(f"[{h.id}] {h.title}" for h in hits[:top_n])
    content = _chat(
        [
            {
                "role": "system",
                "content": "Rank papers by relevance to the query. Return ONLY a JSON array of ids.",
            },
            {"role": "user", "content": f"Query: {query}\nPapers:\n{listing}"},
        ],
        temperature=0.0,
    )
    try:
        order = json.loads(content)
        if isinstance(order, list):
            return [int(x) for x in order]
    except (ValueError, TypeError):
        logger.warning("LLM rerank returned non-JSON: %s", content[:120])
    return []


def summarize_results(query: str, hits: list[SearchHit]) -> tuple[list[SearchHit], str | None]:
    order = rerank(query, hits)
    by_id = {h.id: h for h in hits}
    if order:
        reordered = [by_id[i] for i in order if i in by_id]
        reordered += [h for h in hits if h.id not in set(order)]
    else:
        reordered = hits

    titles = [h.title for h in reordered[:20]]
    try:
        summary = summarize_field(query, titles)
    except Exception:
        summary = None
    return reordered, summary
