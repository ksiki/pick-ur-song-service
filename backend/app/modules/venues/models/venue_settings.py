from typing import TYPE_CHECKING

from app.db.models import BaseModel
from tortoise import fields
from tortoise.fields.relational import OneToOneRelation
from tortoise.validators import MaxValueValidator, MinValueValidator

if TYPE_CHECKING:
    from app.modules.venues.models import Venue


class VenueSettings(BaseModel):
    venue: OneToOneRelation["Venue"] = fields.OneToOneField(
        "models.Venue", related_name="settings", on_delete=fields.CASCADE, pk=True
    )

    allow_explicit = fields.BooleanField(default=False)

    commission_fee_percent = fields.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=50.00,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
        description="Service commission in percentage (from 0.00 to 100.00)",
    )

    track_price = fields.DecimalField(max_digits=10, decimal_places=2, default=3.00)
    track_price_no_queue = fields.DecimalField(max_digits=10, decimal_places=2, default=6.00)

    timezone = fields.CharField(
        max_length=50,
        default="Europe/Minsk",
        description="The time zone of the establishment (for example, Europe/Minsk)",
    )

    class Meta:
        table = "venue_settings"
