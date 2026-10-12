"""Upsert embedded works into a Weaviate collection."""

import logging
from typing import Any

from apps.api.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def connect() -> Any | None:
    if not settings.weaviate_url:
        logger.warning("WEAVIATE_URL not set; skipping vector store upsert")
        return None
    import weaviate
    from weaviate.classes.init import Auth

    auth = Auth.api_key(settings.weaviate_api_key) if settings.weaviate_api_key else None
    return weaviate.connect_to_weaviate_cloud(
        cluster_url=settings.weaviate_url, auth_credentials=auth
    )


def ensure_collection(client: Any) -> Any:
    from weaviate.classes.config import DataType, Property

    if client.collections.exists(settings.weaviate_class):
        return client.collections.get(settings.weaviate_class)
    return client.collections.create(
        name=settings.weaviate_class,
        properties=[
            Property(name="work_id", data_type=DataType.INT),
            Property(name="title", data_type=DataType.TEXT),
            Property(name="abstract", data_type=DataType.TEXT),
            Property(name="publication_year", data_type=DataType.INT),
            Property(name="cited_by_count", data_type=DataType.INT),
            Property(name="doi", data_type=DataType.TEXT),
            Property(name="source", data_type=DataType.TEXT),
        ],
    )


def upsert(client: Any, collection: Any, rows: list[dict]) -> int:
    from weaviate.classes.data import DataObject

    objects = [
        DataObject(properties=row["properties"], vector=row["vector"]) for row in rows
    ]
    result = collection.data.insert_many(objects)
    if getattr(result, "errors", None):
        logger.warning("Weaviate insert errors: %s", result.errors)
    return len(objects)
