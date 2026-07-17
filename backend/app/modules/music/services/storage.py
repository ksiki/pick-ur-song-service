from uuid import UUID

from app.modules.music.models import Playlist
from app.modules.music.models.playlist_track import PlaylistTrack


class MusicStorageService:
    """
    Хранилище всех плейлистов и треков бара. Нужен для получения метаданных.
    """

    @staticmethod
    async def get_playlist_tracks(playlist_id: UUID) -> list[PlaylistTrack]:
        """
        Возвращает отсортированные песни конкретного плейлиста.
        """
        return await PlaylistTrack.filter(playlist_id=playlist_id).order_by("sort_order")

    @staticmethod
    async def get_venue_playlists(venue_id: UUID) -> list[Playlist]:
        """
        Возвращает плейлисты бара с предзагруженными в них треками
        """
        query = Playlist.filter(venue_id=venue_id)
        return await query.prefetch_related("tracks")
