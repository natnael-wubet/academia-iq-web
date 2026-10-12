from typing import Any

from apps.api.core.config import get_settings
from apps.api.services.base import BaseClient

settings = get_settings()


class CrossrefClient(BaseClient):
    base_url = "https://api.crossref.org"

    def __init__(self) -> None:
        super().__init__(mailto=settings.mailto)

    async def search_works(
        self,
        query: str,
        rows: int = 50,
        offset: int = 0,
        filters: dict[str, Any] | None = None,
    ) -> list[dict]:
        params: dict[str, Any] = {"query": query, "rows": rows, "offset": offset}
        if filters:
            params["filter"] = ",".join(f"{k}:{v}" for k, v in filters.items())
        data = await self.get("/works", params)
        return data.get("message", {}).get("items", [])

    async def fetch_doi(self, doi: str) -> dict:
        data = await self.get(f"/works/{doi}")
        return data.get("message", {})

    def normalize_work(self, raw: dict) -> dict:
        title = raw.get("title") or []
        abstract = raw.get("abstract")
        authors = raw.get("author") or []
        issued = (raw.get("issued") or {}).get("date-parts") or [[None]]
        year = issued[0][0] if issued and issued[0] else None
        container = raw.get("container-title") or []
        return {
            "doi": (raw.get("DOI") or "").lower() or None,
            "title": title[0] if title else "",
            "abstract": abstract,
            "publication_year": year,
            "cited_by_count": raw.get("is-referenced-by-count", 0),
            "reference_count": raw.get("references-count", 0),
            "type": raw.get("type"),
            "venue": {"name": container[0], "issn_l": (raw.get("ISSN") or [None])[0]}
            if container
            else None,
            "authors": [
                {
                    "display_name": " ".join(
                        filter(None, [a.get("given"), a.get("family")])
                    )
                    or a.get("name", ""),
                    "orcid": (a.get("ORCID") or "").replace("http://orcid.org/", "")
                    or None,
                }
                for a in authors
            ],
            "source": "crossref",
        }
