from typing import Final

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DOMEN: str = "localhost"

    SMTP_HOST: str = "mailpit"
    SMTP_PORT: int = 1025
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_FROM_EMAIL: str = "noreply@yourdomain.com"

    DATABASE_URL: str = "postgres://pus_user:pus_pass@localhost:5432/pus_db"

    ENVIRONMENT: str = "development"
    SENTRY_DSN: str | None = None

    FRONTEND_URLS: list[str] = ["http://localhost:80", "http://localhost:3000"]

    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"
    REDIS_URL: str = "redis://localhost:6379/0"

    SECRET_KEY: str = "b317936085b0dcb5fe5929e70369cd40b11cf2a23c669f0c069e2eadc2eb2faf"
    ALGORITHM: str = "HS256"
    EMAIL_TOKEN_EXPIRE_HOURS: int = 24  # Время жизни токена подтверждения почты (в часах)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # Время жизни обычного Access Token (для авторизации)
    REFRESH_TOKEN_EXPIRE_DAYS: int = 15  # Время жизни Refresh Token для сессии  (в днях)

    STREAM_CHUNK_SIZE: int = Field(default=65536, description="64KB chunks")
    STREAM_MAX_RETRIES: int = Field(default=3)
    STREAM_RETRY_DELAY: float = Field(default=1.0)

    S3_ENDPOINT_URL: str = "http://minio:9000"
    S3_ACCESS_KEY: str = "admin"
    S3_SECRET_KEY: str = "password123"
    S3_REGION_NAME: str = Field(default="us-east-1")
    S3_BUCKET_BACKGROUNDS: str = Field(default="reports")
    S3_PRESIGNED_EXPIRES_IN: int = Field(default=1800, description="30 minutes TTL")

    MODERATION_TRACK_EXPIRE_SECONDS: int = 3600 * 24

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings: Final[Settings] = Settings()
