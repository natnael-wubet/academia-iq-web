from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Academia IQ"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"

    database_url: str = "postgresql+psycopg://academia:academia@localhost:5432/academia_iq"
    redis_url: str = "redis://localhost:6379/0"

    weaviate_url: str = ""
    weaviate_api_key: str = ""
    weaviate_class: str = "Paper"

    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    semantic_scholar_api_key: str = ""

    # Polite-pool contact for OpenAlex / Crossref.
    mailto: str = "hello@academia-iq.dev"

    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_dim: int = 384

    cache_ttl_seconds: int = 3600
    rate_limit_per_minute: int = 60


@lru_cache
def get_settings() -> Settings:
    return Settings()
