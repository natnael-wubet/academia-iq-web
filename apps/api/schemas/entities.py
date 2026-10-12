from datetime import date

from pydantic import BaseModel, ConfigDict


class InstitutionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    country_code: str | None = None
    type: str | None = None
    works_count: int = 0
    cited_by_count: int = 0


class AuthorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    display_name: str
    orcid: str | None = None
    openalex_id: str | None = None
    works_count: int = 0
    cited_by_count: int = 0
    h_index: int | None = None
    institution: InstitutionOut | None = None


class VenueOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    issn_l: str | None = None
    type: str | None = None
    works_count: int = 0


class WorkOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    abstract: str | None = None
    doi: str | None = None
    publication_date: date | None = None
    publication_year: int | None = None
    cited_by_count: int = 0
    is_open_access: bool = False
    source: str | None = None
    venue: VenueOut | None = None
    authors: list[AuthorOut] = []


class TrendPoint(BaseModel):
    year: int
    works: int
    citations: int


class CitationGraphOut(BaseModel):
    nodes: list[dict]
    edges: list[dict]
    pagerank: dict[int, float] = {}
    communities: dict[int, int] = {}
