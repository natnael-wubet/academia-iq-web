import asyncio
import logging
import random
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class ApiError(RuntimeError):
    """Raised when an upstream API cannot be reached after retries."""


class BaseClient:
    """Async HTTP client with retries, backoff, and polite-pool headers."""

    base_url: str = ""
    timeout: float = 30.0
    max_retries: int = 4

    def __init__(self, mailto: str | None = None) -> None:
        self._mailto = mailto
        headers = {"User-Agent": "AcademiaIQ/1.0"}
        if mailto:
            headers["User-Agent"] = f"AcademiaIQ/1.0 (mailto:{mailto})"
        self._client = httpx.AsyncClient(
            base_url=self.base_url, timeout=self.timeout, headers=headers
        )

    async def aclose(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> "BaseClient":
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.aclose()

    async def get(self, url: str, params: dict[str, Any] | None = None) -> dict:
        params = {k: v for k, v in (params or {}).items() if v is not None}
        if self._mailto:
            params.setdefault("mailto", self._mailto)
        last_exc: Exception | None = None
        for attempt in range(self.max_retries):
            try:
                resp = await self._client.get(url, params=params)
                if resp.status_code == 429 or resp.status_code >= 500:
                    raise ApiError(f"upstream {resp.status_code}")
                resp.raise_for_status()
                return resp.json()
            except (httpx.HTTPError, ApiError) as exc:
                last_exc = exc
                backoff = min(2 ** attempt + random.random(), 30)
                logger.warning("GET %s failed (%s), retry in %.1fs", url, exc, backoff)
                await asyncio.sleep(backoff)
        raise ApiError(f"GET {url} failed after {self.max_retries} attempts") from last_exc
