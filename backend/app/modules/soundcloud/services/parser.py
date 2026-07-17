import logging
import re
from typing import Any

from app.modules.soundcloud.schemas import SoundCloudTrack

logger = logging.getLogger(__name__)


class SoundCloudParser:
    """
    Парсер для обработки сырых данных от API SoundCloud.
    Отвечает за маппинг полей и фильтрацию нерелевантного контента (ремиксы, каверы и т.д.).
    """

    REMIX_PATTERN = re.compile(
        r"\b(remix|bootleg|mashup|edit|sped up|slowed|reverb|cover|mix|flip)\b",
        re.IGNORECASE,
    )

    @classmethod
    def is_original(cls, title: str, query: str) -> bool:
        """
        Проверяет, является ли трек оригиналом.
        Если нежелательное слово есть в названии трека,
        но ОТСУТСТВУЕТ в поисковом запросе — это не оригинал.
        """
        title_lower = title.lower()
        query_lower = query.lower()

        matches = cls.REMIX_PATTERN.findall(title_lower)
        if not matches:
            return True

        return all(match in query_lower for match in matches)

    @classmethod
    def parse_tracks(cls, raw_data: dict[str, Any], query: str) -> list[SoundCloudTrack]:
        """
        Преобразует сырой JSON-ответ SoundCloud в список валидированных схем SoundCloudTrack,
        сразу отсеивая ремиксы (если они не запрашивались).
        """
        tracks: list[SoundCloudTrack] = []
        collection = raw_data.get("collection", [])

        for item in collection:
            if item.get("kind") != "track":
                continue

            title = item.get("title", "")
            artist = item.get("user", {}).get("username", "")

            if not cls.is_original(title, query):
                continue

            duration_ms = item.get("duration", 0)
            if duration_ms == 0:
                continue

            artwork_url = item.get("artwork_url")
            if artwork_url:
                artwork_url = artwork_url.replace("-large", "-t500x500")

            is_explicit = False

            track_id = item.get("id")
            track_url = item.get("permalink_url", "")

            if not track_id or not track_url:
                continue

            try:
                track = SoundCloudTrack(
                    track_id=track_id,
                    track_url=track_url,
                    title=title,
                    artist=artist,
                    duration_ms=duration_ms,
                    artwork_url=artwork_url,
                    is_explicit=is_explicit,
                )
                tracks.append(track)
            except Exception as e:
                logger.warning(f"Ошибка валидации трека {track_id}: {e}")
                continue

        return tracks
