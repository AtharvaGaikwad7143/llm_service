from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    gemini_api_key: str
    database_url: str
    celery_broker_url: str
    redis_url: str
    rag_cache_ttl: int = 300
    model_config = SettingsConfigDict(
        env_file=".env"
    )


settings = Settings()