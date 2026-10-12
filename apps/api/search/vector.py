import logging
from typing import Any

from apps.api.core.config import get_settings
from apps.api.schemas.common import SearchHit

logger = logging.getLogger(__name__)
settings = get_settings()


class VectorSearch:
    """Weaviate-backed semantic search with an in-process fallback."""

    def __init__(self) -> None:
        self._client: Any | None = None

    @property
    def client(self) -> Any | None:
        if self._client is None and settings.weaviate_url:
            try:
                import weaviate
                from weaviate.classes.init import Auth

                auth = (
                    Auth.api_key(settings.weaviate_api_key)
                    if settings.weaviate_api_key
                    else None
                )
                self._client = weaviate.connect_to_weaviate_cloud(
                    cluster_url=settings.weaviate_url,
                    auth_credentials=auth,
                )
            except Exception as exc:  # pragma: no cover - depends on env
                logger.warning("Weaviate unavailable, vector search degraded: %s", exc)
                self._client = None
        return self._client

    def search(
        self,
        vector: list[float],
        limit: int = 50,
        year_from: int | None = None,
        year_to: int | None = None,
    ) -> list[SearchHit]:
        client = self.client
        if client is None:
            return []
        from weaviate.classes.query import Filter, MetadataQuery

        collection = client.collections.get(settings.weaviate_class)
        where = None
        conditions = []
        if year_from is not None:
            conditions.append(Filter.by_property("publication_year").greater_or_equal(year_from))
        if year_to is not None:
            conditions.append(Filter.by_property("publication_year").less_or_equal(year_to))
        if conditions:
            where = conditions[0]
            for c in conditions[1:]:
                where = where & c

        result = collection.query.near_vector(
            near_vector=vector,
            limit=limit,
            filters=where,
            return_metadata=MetadataQuery(distance=True),
        )
        hits: list[SearchHit] = []
        for i, obj in enumerate(result.objects):
            props = obj.properties
            distance = obj.metadata.distance or 0.0
            hits.append(
                SearchHit(
                    id=int(props["work_id"]),
                    title=props.get("title", ""),
                    abstract=props.get("abstract"),
                    publication_year=props.get("publication_year"),
                    cited_by_count=props.get("cited_by_count", 0),
                    doi=props.get("doi"),
                    score=1.0 - float(distance),
                    source=props.get("source"),
                    vector_rank=i,
                )
            )
        return hits


vector_search = VectorSearch()
