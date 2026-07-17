from enum import IntEnum
from typing import TYPE_CHECKING

import uuid6
from app.db.models import BaseModel
from tortoise import fields
from tortoise.fields.relational import ForeignKeyRelation

if TYPE_CHECKING:
    from app.modules.venues.models import Venue


class DayOfWeek(IntEnum):
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7


class VenueSchedule(BaseModel):
    id = fields.UUIDField(pk=True, default=uuid6.uuid7)

    venue: ForeignKeyRelation["Venue"] = fields.ForeignKeyField(
        "models.Venue", related_name="schedules", on_delete=fields.CASCADE
    )

    day_of_week = fields.IntEnumField(
        enum_type=DayOfWeek, description="Day of the week (1 - Monday, 7 - Sunday)"
    )

    open_time = fields.TimeField(null=True, description="Opening time")
    close_time = fields.TimeField(null=True, description="Closing time")

    is_day_off = fields.BooleanField(
        default=False, description="Day off (the establishment is closed)"
    )

    class Meta:
        table = "venue_schedules"
        unique_together = (("venue_id", "day_of_week"),)
