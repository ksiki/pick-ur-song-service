from enum import Enum
from typing import TYPE_CHECKING

import uuid6
from app.db.models import BaseModel
from tortoise import fields
from tortoise.fields.relational import ForeignKeyRelation
from tortoise.indexes import Index

if TYPE_CHECKING:
    from app.modules.venues.models import Venue


class BlacklistItemType(str, Enum):
    ARTIST = "artist"
    KEYWORD = "keyword"


class VenueBlacklist(BaseModel):
    id = fields.UUIDField(pk=True, default=uuid6.uuid7)

    venue: ForeignKeyRelation["Venue"] = fields.ForeignKeyField(
        "models.Venue", related_name="blacklists", on_delete=fields.CASCADE
    )

    item_type = fields.CharEnumField(enum_type=BlacklistItemType, description="Block type")

    item_value = fields.CharField(max_length=255)

    class Meta:
        table = "venue_blacklists"
        indexes = [Index(fields=("venue_id", "item_type"))]
