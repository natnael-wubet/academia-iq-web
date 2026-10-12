from typing import Any

from apps.api.core.config import get_settings
from apps.api.services.base import BaseClient

settings = get_settings()


def _reconstruct_abstract(inverted_index: dict[str, list[int]] | None) -> str | None:
    if not inverted_index:
        return None
    positions: list[tuple[int, str]] = []
    for word, idxs in inverted_index.items():
        positions.extend((i, word) for i in idxs)
    positions.sort()
    return " ".join(word for _, word in positions)


class OpenAlexClient(BaseClient):
    base_url = "https://api.openalex.org"

    def __init__(self) -> None:
        super().__init__(mailto=settings.mailto)

    async def search_works(
        self,
        query: str,
        per_page: int = 50,
        page: int = 1,
        filters: str | None = None,
    ) -> list[dict]:
        params: dict[str, Any] = {
            "search": query,
            "per-page": per_page,
            "page": page,
            "select": ",".join(
                [
                    "id", "doi", "title", "display_name", "publication_date",
                    "publication_year", "cited_by_count", "referenced_works",
                    "authorships", "abstract_inverted_index", "type",
                    "language", "open_access", "primary_location",
                ]
            ),
        }
        if filters:
            params["filter"] = filters
        data = await self.get("/works", params)
        return data.get("results", [])

    async def fetch_work(self, openalex_id: str) -> dict:
        return await self.get(f"/works/{openalex_id}")

    async def fetch_author(self, openalex_id: str) -> dict:
        return await self.get(f"/authors/{openalex_id}")

    async def search_authors(self, query: str, per_page: int = 25) -> list[dict]:
        data = await self.get("/authors", {"search": query, "per-page": per_page})
        return data.get("results", [])

    async def fetch_institution(self, openalex_id: str) -> dict:
        return await self.get(f"/institutions/{openalex_id}")

    def normalize_work(self, raw: dict) -> dict:
        primary = raw.get("primary_location") or {}
        source = (primary.get("source") or {}) if primary else {}
        open_access = raw.get("open_access") or {}
        authorships = raw.get("authorships") or []
        return {
            "openalex_id": raw.get("id"),
            "doi": (raw.get("doi") or "").replace("https://doi.org/", "") or None,
            "title": raw.get("title") or raw.get("display_name") or "",
            "abstract": _reconstruct_abstract(raw.get("abstract_inverted_index")),
            "publication_date": raw.get("publication_date"),
            "publication_year": raw.get("publication_year"),
            "cited_by_count": raw.get("cited_by_count", 0),
            "reference_count": len(raw.get("referenced_works") or []),
            "type": raw.get("type"),
            "language": raw.get("language"),
            "is_open_access": bool(open_access.get("is_oa")),
            "venue": {
                "openalex_id": source.get("id"),
                "name": source.get("display_name"),
                "issn_l": source.get("issn_l"),
                "type": source.get("type"),
            }
            if source
            else None,
            "authors": [
                {
                    "openalex_id": (a.get("author") or {}).get("id"),
                    "display_name": (a.get("author") or {}).get("display_name") or "",
                    "orcid": (a.get("author") or {}).get("orcid"),
                    "position": a.get("author_position"),
                    "institutions": [
                        {
                            "openalex_id": inst.get("id"),
                            "name": inst.get("display_name") or "",
                            "country_code": inst.get("country_code"),
                            "type": inst.get("type"),
                        }
                        for inst in (a.get("institutions") or [])
                    ],
                }
                for a in authorships
            ],
            "referenced_works": raw.get("referenced_works") or [],
            "source": "openalex",
        }
