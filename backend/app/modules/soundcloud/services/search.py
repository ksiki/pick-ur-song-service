import logging
from uuid import UUID

from app.modules.music.services.moderation import ModerationService
from app.modules.soundcloud.schemas import SoundCloudSearchResponse, SoundCloudTrack
from app.modules.soundcloud.services.client import SoundCloudClient
from app.modules.soundcloud.services.parser import SoundCloudParser
from app.modules.venues.models.venue_settings import VenueSettings

logger = logging.getLogger(__name__)


class SoundCloudSearchService:
    """
    Сервис-оркестратор поиска треков в SoundCloud.
    Объединяет HTTP-клиент, парсер и локальную модерацию заведения.
    """

    @classmethod
    async def search_tracks(
        cls,
        query: str,
        venue_id: UUID,
        venue_settings: VenueSettings,
        limit: int = 30,
    ) -> SoundCloudSearchResponse:
        """
        Ищет треки по запросу, фильтрует ремиксы (через парсер)
        и массово прогоняет через алгоритмы модерации заведения.
        """
        params = {
            "q": query,
            "limit": limit,
        }

        try:
            raw_data = await SoundCloudClient.request("/search/tracks", params=params)
        except Exception as e:
            logger.error(f"Ошибка при запросе к SoundCloud API для '{query}': {e}")
            return SoundCloudSearchResponse(query=query, total_found=0, items=[])

        parsed_tracks = SoundCloudParser.parse_tracks(raw_data, query)

        if not parsed_tracks:
            return SoundCloudSearchResponse(query=query, total_found=0, items=[])

        moderation_results = await ModerationService.bulk_check_tracks(
            venue_id=venue_id,
            venue_settings=venue_settings,
            tracks=parsed_tracks,
        )

        allowed_tracks: list[SoundCloudTrack] = []

        for track, mod_result in zip(parsed_tracks, moderation_results, strict=False):
            if mod_result.is_allowed:
                allowed_tracks.append(track)
            else:
                logger.debug(
                    f"Трек {track.track_id} ({track.title}) отфильтрован. "
                    f"Причина: {mod_result.reason}"
                )

        return SoundCloudSearchResponse(
            query=query,
            total_found=len(allowed_tracks),
            items=allowed_tracks,
        )
