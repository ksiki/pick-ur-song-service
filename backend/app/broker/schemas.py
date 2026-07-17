from pydantic import UUID4, BaseModel

from app.modules.music.schemas import TrackSourceType


class PlayTrackCommand(BaseModel):
    """
    Команда, которая транслируется через RabbitMQ Fanout во все инстансы бэкенда,
    чтобы нужный воркер перехватил ее и отправил по WebSocket в плеер заведения.
    """

    venue_id: UUID4
    order_id: UUID4 | None = None
    track_id: int
    track_url: str
    title: str
    artist: str
    artwork_url: str | None = None
    duration_ms: int
    source_type: TrackSourceType
