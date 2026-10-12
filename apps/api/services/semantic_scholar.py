from typing import Any

from apps.api.core.config import get_settings
from apps.api.services.base import BaseClient

settings = get_settings()

FIELDS = ",".join(
    [
        "paperId", "externalIds", "title", "abstract", "year", "publicationDate",
        "citationCount", "referenceCount", "venue", "openAccessPdf",
        "authors", "fieldsOfStudy", "embedding",
    ]
)


class SemanticScholarClient(BaseClient):
    base_url = "https://api.semanticscholar.org/graph/v1"

    def __init__(self) -> None:
        super().__init__(mailto=settings.mailto)
        if settings.semantic_scholar_api_key:
            self._client.headers["x-api-key"] = settings.semantic_scholar_api_key

    async def search_papers(
        self, query: str, limit: int = 50, offset: int = 0, fields: str = FIELDS
    ) -> list[dict]:
        data = await self.get(
            "/paper/search",
            {"query": query, "limit": limit, "offset": offset, "fields": fields},
        )
        return data.get("data", [])

    async def fetch_paper(self, paper_id: str, fields: str = FIELDS) -> dict:
        return await self.get(f"/paper/{paper_id}", {"fields": fields})

    async def recommendations(self, paper_id: str, limit: int = 20) -> list[dict]:
        data = await self.get(
            f"/recommendations/v1/papers/forpaper/{paper_id}",
            {"limit": limit, "fields": FIELDS},
        )
        return data.get("recommendedPapers", [])

    async def fetch_author(self, author_id: str) -> dict:
        return await self.get(
            f"/author/{author_id}",
            {"fields": "name,affiliations,paperCount,citationCount,hIndex,externalIds"},
        )

    def normalize_paper(self, raw: dict) -> dict:
        external = raw.get("externalIds") or {}
        authors = raw.get("authors") or []
        return {
            "semantic_scholar_id": raw.get("paperId"),
            "doi": external.get("DOI"),
            "title": raw.get("title") or "",
            "abstract": raw.get("abstract"),
            "publication_date": raw.get("publicationDate"),
            "publication_year": raw.get("year"),
            "cited_by_count": raw.get("citationCount", 0),
            "reference_count": raw.get("referenceCount", 0),
            "type": "article",
            "is_open_access": bool(raw.get("openAccessPdf")),
            "venue": {"name": raw.get("venue")} if raw.get("venue") else None,
            "authors": [
                {
                    "semantic_scholar_id": a.get("authorId"),
                    "display_name": a.get("name") or "",
                }
                for a in authors
            ],
            "fields_of_study": raw.get("fieldsOfStudy") or [],
            "embedding": raw.get("embedding"),
            "source": "semantic_scholar",
        }
