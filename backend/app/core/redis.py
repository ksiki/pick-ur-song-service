from collections.abc import AsyncGenerator
from typing import Final

import redis.asyncio as aioredis

from app.core.config import settings


class RedisCache:
    def __init__(self) -> None:
        self.client: aioredis.Redis | None = None

    def init(self) -> None:
        """
        Инициализация пула соединений Redis
        """
        self.client = aioredis.Redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            max_connections=30,
            retry_on_timeout=True,
            health_check_interval=30,
        )

    async def close(self) -> None:
        if self.client:
            await self.client.close()

    @property
    def safe_client(self) -> aioredis.Redis:
        if self.client is None:
            raise RuntimeError("Redis client is not initialized. Call init() first.")
        return self.client


redis_cache: Final[RedisCache] = RedisCache()


async def get_redis() -> AsyncGenerator[aioredis.Redis, None]:
    """Dependency для FastAPI роутеров"""
    yield redis_cache.safe_client
