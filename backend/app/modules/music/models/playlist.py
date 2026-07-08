from typing import TYPE_CHECKING

import uuid6
from app.db.models import TimestampMixin
from tortoise import fields
from tortoise.fields.relational import ForeignKeyRelation
from tortoise.indexes import Index

if TYPE_CHECKING:
    from app.modules.bars.models import Bar


class Playlist(TimestampMixin):
    id = fields.UUIDField(pk=True, default=uuid6.uuid7)

    bar: ForeignKeyRelation["Bar"] = fields.ForeignKeyField(
        "models.Bar", related_name="playlists", on_delete=fields.CASCADE
    )

    name = fields.CharField(max_length=100)
    is_active = fields.BooleanField(default=False)

    class Meta:
        table = "playlists"
        indexes = [
            Index(fields=("bar_id", "is_active"), name="idx_playlist_bar_active"),
        ]
