from app.api.schemas import TrackMeta
from pydantic import BaseModel


class SoundCloudTrack(TrackMeta):
    """
    Внутренняя схема трека, полученного из SoundCloud.
    Содержит флаг is_explicit для дальнейшей передачи в ModerationService.
    """

    is_explicit: bool = False


class SoundCloudSearchResponse(BaseModel):
    """
    Схема ответа для эндпоинта поиска треков.
    """

    query: str
    total_found: int
    items: list[SoundCloudTrack]
