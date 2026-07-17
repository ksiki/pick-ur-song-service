import json
import logging
from typing import Any
from uuid import UUID

from app.core.config import settings
from app.core.redis import redis_cache
from app.modules.music.models import BlacklistItemType, VenueBlacklist
from app.modules.soundcloud.schemas import SoundCloudTrack
from app.modules.venues.models import VenueSettings

logger = logging.getLogger(__name__)


class ModerationResult:
    """Простая структура для кэширования результата проверки"""

    def __init__(self, is_allowed: bool, reason: str | None = None):
        self.is_allowed = is_allowed
        self.reason = reason

    def to_dict(self) -> dict[str, Any]:
        return {"is_allowed": self.is_allowed, "reason": self.reason}


class ModerationService:
    """
    Сервис алгоритмической модерации контента.
    Оптимизирован для массовой проверки треков (Bulk).
    """

    @staticmethod
    def _get_cache_key(venue_id: UUID, track_id: int) -> str:
        return f"moderation:{venue_id}:track:{track_id}"

    @staticmethod
    def _run_moderation_logic(
        settings: VenueSettings,
        blacklists: list[VenueBlacklist],
        track_title: str,
        track_artist: str,
        is_explicit: bool,
    ) -> ModerationResult:
        """
        Синхронная логика проверки одного трека в памяти.
        База данных сюда не ходит, списки передаются аргументом.
        """
        if is_explicit and not settings.allow_explicit:
            return ModerationResult(False, "Трек содержит ненормативную лексику (Explicit).")

        title_lower = track_title.lower()
        artist_lower = track_artist.lower()

        for item in blacklists:
            value = item.item_value.lower()
            if item.item_type == BlacklistItemType.ARTIST and value in artist_lower:
                return ModerationResult(False, f"Исполнитель '{track_artist}' в черном списке.")

            if item.item_type == BlacklistItemType.KEYWORD and value in title_lower:
                return ModerationResult(False, "Название трека содержит запрещенные слова.")

        return ModerationResult(True)

    @classmethod
    async def bulk_check_tracks(
        cls,
        venue_id: UUID,
        venue_settings: VenueSettings,
        tracks: list[SoundCloudTrack],
    ) -> list[ModerationResult]:
        """
        Массовая проверка списка треков с использованием Redis MGET.
        Минимизирует количество коннектов к Redis и БД.
        """
        if not tracks:
            return []

        cache_keys = [cls._get_cache_key(venue_id, t.track_id) for t in tracks]
        cached_data = await redis_cache.safe_client.mget(*cache_keys)

        results: list[ModerationResult | None] = [None] * len(tracks)
        tracks_to_check = []

        for i, cached_val in enumerate(cached_data):
            if cached_val:
                data = json.loads(cached_val)
                results[i] = ModerationResult(
                    is_allowed=data["is_allowed"], reason=data.get("reason")
                )
            else:
                tracks_to_check.append((i, tracks[i]))

        if tracks_to_check:
            blacklists = await VenueBlacklist.filter(venue_id=venue_id)

            pipeline = redis_cache.safe_client.pipeline()

            for idx, track in tracks_to_check:
                res = cls._run_moderation_logic(
                    settings=venue_settings,
                    blacklists=blacklists,
                    track_title=track.title,
                    track_artist=track.artist,
                    is_explicit=track.is_explicit,
                )
                results[idx] = res

                pipeline.setex(
                    cache_keys[idx],
                    settings.MODERATION_TRACK_EXPIRE_SECONDS,
                    json.dumps(res.to_dict()),
                )

            await pipeline.execute()

        return [r for r in results if r is not None]
