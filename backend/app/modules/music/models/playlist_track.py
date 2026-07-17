from typing import TYPE_CHECKING

import uuid6
from app.db.models import BaseModel
from tortoise import fields
from tortoise.fields.relational import ForeignKeyRelation
from tortoise.indexes import Index

if TYPE_CHECKING:
    from app.modules.music.models import Playlist


class PlaylistTrack(BaseModel):
    id = fields.UUIDField(pk=True, default=uuid6.uuid7)

    playlist: ForeignKeyRelation["Playlist"] = fields.ForeignKeyField(
        "models.Playlist", related_name="tracks", on_delete=fields.CASCADE
    )

    track_id = fields.CharField(max_length=255)

    track_url = fields.CharField(max_length=255)

    title = fields.CharField(max_length=255)

    artwork_url = fields.CharField(max_length=512, null=True)

    artist = fields.CharField(max_length=255)

    duration_ms = fields.IntField()

    sort_order = fields.IntField()

    class Meta:
        table = "playlist_tracks"
        indexes = [Index(fields=("playlist_id", "sort_order"))]
