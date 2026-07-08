from typing import Final

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "postgres://pus_user:pus_pass@localhost:5432/pus_db"

    ENVIRONMENT: str = "development"
    SENTRY_DSN: str | None = None

    FRONTEND_URLS: list[str] = ["http://localhost:80", "http://localhost:3000"]

    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"
    REDIS_URL: str = "redis://localhost:6379/0"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings: Final[Settings] = Settings()
