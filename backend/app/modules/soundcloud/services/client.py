import asyncio
import logging
import random
import re
from typing import Any

import httpx
from app.core.exceptions import SoundCloudClientError
from app.core.redis import redis_cache
from app.modules.soundcloud.models.proxy import Proxy
from redis.asyncio.lock import Lock

logger = logging.getLogger(__name__)


class SoundCloudClient:
    """
    Отказоустойчивый HTTP-клиент для взаимодействия с API SoundCloud
    """

    SC_BASE_URL: str = "https://api-v2.soundcloud.com"
    SC_WEB_URL: str = "https://soundcloud.com"

    CLIENT_ID_KEY: str = "soundcloud:client_id"
    CLIENT_ID_LOCK_KEY: str = "soundcloud:client_id:lock"

    MAX_RETRIES: int = 3
    TIMEOUT: httpx.Timeout = httpx.Timeout(10.0)

    @staticmethod
    async def _get_random_proxy() -> Proxy | None:
        """Получает случайный активный прокси из БД."""
        proxies = await Proxy.filter(is_active=True, is_banned=False).all()
        if not proxies:
            return None
        return random.choice(proxies)  # noqa: S311

    @staticmethod
    def _format_proxy_url(proxy: Proxy) -> str:
        """Форматирует строку прокси для httpx."""

        auth = f"{proxy.username}:{proxy.password}@" if proxy.username and proxy.password else ""
        return f"{proxy.protocol.value}://{auth}{proxy.ip_address}:{proxy.port}"

    @staticmethod
    async def _mark_proxy_failed(proxy_id: Any) -> None:
        """Помечает прокси как проблемный"""

        logger.warning(f"Прокси {proxy_id} недоступен или заблокирован. Отключаем.")
        await Proxy.filter(id=proxy_id).update(is_active=False)

    @classmethod
    async def _parse_client_id(cls, http_client: httpx.AsyncClient) -> str:
        """Парсит новый client_id с главной страницы SoundCloud."""
        logger.info("Парсинг нового client_id SoundCloud...")
        response = await http_client.get(cls.SC_WEB_URL)
        response.raise_for_status()

        scripts = re.findall(
            r'<script crossorigin src="(https://a-v2\.sndcdn\.com/assets/[^"]+\.js)"></script>',
            response.text,
        )
        if not scripts:
            raise SoundCloudClientError("Не удалось найти JS-скрипты на главной странице")

        for script_url in reversed(scripts):
            js_resp = await http_client.get(script_url)
            if js_resp.status_code == 200:
                match = re.search(r'client_id:"([a-zA-Z0-9]{32})"', js_resp.text)
                if match:
                    return match.group(1)

        raise SoundCloudClientError("Не удалось извлечь client_id из JS-скриптов")

    @classmethod
    async def get_client_id(cls) -> str:
        """
        Получает client_id из кэша. Если нет — парсит новый с использованием Redis Lock,
        чтобы избежать гонки (thundering herd), когда 100 запросов одновременно пойдут парсить.
        """
        redis = redis_cache.safe_client
        client_id = await redis.get(cls.CLIENT_ID_KEY)

        if client_id:
            return client_id.decode("utf-8") if isinstance(client_id, bytes) else client_id

        lock = Lock(redis, cls.CLIENT_ID_LOCK_KEY, timeout=15)

        async with lock:
            client_id = await redis.get(cls.CLIENT_ID_KEY)
            if client_id:
                return client_id.decode("utf-8") if isinstance(client_id, bytes) else client_id

            async with httpx.AsyncClient(timeout=cls.TIMEOUT) as http_client:
                new_client_id = await cls._parse_client_id(http_client)

            await redis.setex(cls.CLIENT_ID_KEY, 86400, new_client_id)
            logger.info(f"Получен новый client_id: {new_client_id}")
            return new_client_id

    @classmethod
    async def invalidate_client_id(cls) -> None:
        """Сбрасывает client_id в случае 401 ошибки."""
        logger.warning("Инвалидация текущего client_id SoundCloud.")
        await redis_cache.safe_client.delete(cls.CLIENT_ID_KEY)

    @classmethod
    async def request(cls, endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Выполняет запрос к API SoundCloud с автоматической подстановкой client_id,
        ротацией прокси и ретраями.
        """
        if params is None:
            params = {}

        for attempt in range(cls.MAX_RETRIES):
            proxy = await cls._get_random_proxy()
            proxy_url = cls._format_proxy_url(proxy) if proxy else None
            client_id = await cls.get_client_id()

            params["client_id"] = client_id
            url = f"{cls.SC_BASE_URL}{endpoint}"

            try:
                async with httpx.AsyncClient(proxy=proxy_url, timeout=cls.TIMEOUT) as http_client:
                    response = await http_client.get(url, params=params)

                    if response.status_code == 401:
                        await cls.invalidate_client_id()
                        continue

                    if response.status_code in (403, 429) and proxy:
                        await cls._mark_proxy_failed(proxy.id)
                        continue

                    response.raise_for_status()
                    return response.json()  # type: ignore[no-any-return]

            except (httpx.RequestError, httpx.TimeoutException) as e:
                logger.error(f"Ошибка сети (попытка {attempt + 1}/{cls.MAX_RETRIES}): {e}")
                if proxy:
                    await cls._mark_proxy_failed(proxy.id)
                if attempt == cls.MAX_RETRIES - 1:
                    raise SoundCloudClientError(
                        f"Сетевая ошибка после {cls.MAX_RETRIES} попыток: {e}"
                    ) from e
                await asyncio.sleep(1)

        raise SoundCloudClientError("Превышено максимальное количество попыток запроса")
