from typing import TYPE_CHECKING

import uuid6
from app.db.models import TimestampMixin
from tortoise import fields
from tortoise.fields.relational import ForeignKeyRelation
from tortoise.indexes import Index

if TYPE_CHECKING:
    from app.modules.venues.models import Venue


class Playlist(TimestampMixin):
    id = fields.UUIDField(pk=True, default=uuid6.uuid7)

    venue: ForeignKeyRelation["Venue"] = fields.ForeignKeyField(
        "models.Venue", related_name="playlists", on_delete=fields.CASCADE
    )

    name = fields.CharField(max_length=100)

    is_active = fields.BooleanField(default=False)

    class Meta:
        table = "playlists"
        indexes = [
            Index(fields=("venue_id", "is_active"), name="idx_playlist_venue_active"),
        ]
