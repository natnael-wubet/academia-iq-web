import functools
import hashlib
import json
import logging
from typing import Any

import redis

from apps.api.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class Cache:
    """Thin Redis wrapper with graceful degradation when Redis is unavailable."""

    def __init__(self, url: str | None = None) -> None:
        self._url = url or settings.redis_url
        self._client: redis.Redis | None = None

    @property
    def client(self) -> redis.Redis | None:
        if self._client is None:
            try:
                self._client = redis.from_url(self._url, decode_responses=True)
                self._client.ping()
            except redis.RedisError as exc:  # pragma: no cover - depends on env
                logger.warning("Redis unavailable, caching disabled: %s", exc)
                self._client = None
        return self._client

    def get(self, key: str) -> Any | None:
        client = self.client
        if client is None:
            return None
        try:
            raw = client.get(key)
        except redis.RedisError:
            return None
        return json.loads(raw) if raw is not None else None

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        client = self.client
        if client is None:
            return
        try:
            client.set(key, json.dumps(value, default=str), ex=ttl or settings.cache_ttl_seconds)
        except redis.RedisError:
            pass

    def incr(self, key: str, ttl: int | None = None) -> int | None:
        client = self.client
        if client is None:
            return None
        try:
            pipe = client.pipeline()
            pipe.incr(key)
            if ttl:
                pipe.expire(key, ttl)
            return pipe.execute()[0]
        except redis.RedisError:
            return None


cache = Cache()


def cache_key(*parts: Any) -> str:
    digest = hashlib.sha256(
        json.dumps(parts, default=str, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return f"aiq:{digest}"


def cached(prefix: str, ttl: int | None = None):
    """Decorator that memoizes JSON-serializable return values in Redis."""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = cache_key(prefix, args, kwargs)
            hit = cache.get(key)
            if hit is not None:
                return hit
            result = func(*args, **kwargs)
            cache.set(key, result, ttl)
            return result

        return wrapper

    return decorator
