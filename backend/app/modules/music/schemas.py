from enum import Enum

from app.api.schemas import TrackMeta
from app.modules.music.models import BlacklistItemType
from pydantic import UUID4, BaseModel, Field


class TrackSourceType(str, Enum):
    BACKGROUND = "BACKGROUND"
    ORDER = "ORDER"
    VIP_ORDER = "VIP_ORDER"


class QueueItem(TrackMeta):
    queue_id: str = Field(..., description="Уникальный ID элемента в очереди (UUID)")
    source_type: TrackSourceType
    order_id: UUID4 | None = None


class BlacklistItemResponse(BaseModel):
    id: UUID4
    item_type: BlacklistItemType
    item_value: str


class AddBlacklistRequest(BaseModel):
    venue_id: UUID4
    item_type: BlacklistItemType
    item_value: str
