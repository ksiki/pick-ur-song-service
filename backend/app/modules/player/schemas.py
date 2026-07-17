from uuid import UUID

from app.api.schemas import TrackMeta
from app.modules.music.schemas import QueueItem, TrackSourceType
from pydantic import BaseModel


class AddTrackRequest(TrackMeta):
    source_type: TrackSourceType
    order_id: UUID | None = None


class AddPlaylistTrackRequest(TrackMeta):
    pass


class PlaylistTrackResponse(TrackMeta):
    id: UUID
    sort_order: int

    class Config:
        from_attributes = True


class PlaylistResponse(BaseModel):
    """Схема плейлиста для списка"""

    id: UUID
    name: str
    is_active: bool

    class Config:
        from_attributes = True


class PlaylistDetailsResponse(PlaylistResponse):
    """Схема плейлиста с вложенными треками (для детального просмотра)"""

    tracks: list[PlaylistTrackResponse]


class ReorderQueueRequest(BaseModel):
    """Схема для Drag-and-Drop"""

    new_order_queue_ids: list[str]


class CreatePlaylistRequest(BaseModel):
    name: str


class LiveQueueResponse(BaseModel):
    """Формат ответа эндпоинта /state для фронтенда плеера"""

    currently_playing: QueueItem | None
    items: list[QueueItem]
