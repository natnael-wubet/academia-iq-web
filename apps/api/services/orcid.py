from apps.api.services.base import BaseClient


class OrcidClient(BaseClient):
    """ORCID public API. No key required; use the public search endpoint."""

    base_url = "https://pub.orcid.org/v3.0"

    def __init__(self) -> None:
        super().__init__(mailto=None)
        self._client.headers["Accept"] = "application/json"

    async def search(self, query: str, rows: int = 25, start: int = 0) -> list[str]:
        data = await self.get("/expanded-search/", {"q": query, "rows": rows, "start": start})
        return [r.get("orcid-id") for r in data.get("expanded-result", []) if r.get("orcid-id")]

    async def fetch_record(self, orcid_id: str) -> dict:
        return await self.get(f"/{orcid_id}/record")

    async def fetch_works(self, orcid_id: str) -> list[dict]:
        data = await self.get(f"/{orcid_id}/works")
        return [g.get("work-summary", [{}])[0] for g in data.get("group", [])]

    async def fetch_employments(self, orcid_id: str) -> list[dict]:
        data = await self.get(f"/{orcid_id}/employments")
        return [g.get("employment-summary", [{}])[0] for g in data.get("affiliation-group", [])]

    async def fetch_educations(self, orcid_id: str) -> list[dict]:
        data = await self.get(f"/{orcid_id}/educations")
        return [g.get("education-summary", [{}])[0] for g in data.get("affiliation-group", [])]

    def normalize_profile(self, orcid_id: str, record: dict) -> dict:
        person = record.get("person") or {}
        name = person.get("name") or {}
        given = (name.get("given-names") or {}).get("value") or ""
        family = (name.get("family-name") or {}).get("value") or ""
        return {
            "orcid": orcid_id,
            "display_name": " ".join(filter(None, [given, family])),
        }
