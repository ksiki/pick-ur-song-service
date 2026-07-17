from pydantic import BaseModel, ConfigDict


class TrackMeta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    track_id: int
    track_url: str
    title: str
    artist: str
    duration_ms: int
    artwork_url: str | None = None
