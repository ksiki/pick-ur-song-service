from enum import Enum
from typing import TYPE_CHECKING

import uuid6
from app.db.models import TimestampMixin
from tortoise import fields
from tortoise.fields.relational import ForeignKeyRelation

if TYPE_CHECKING:
    from app.modules.venues.models import Venue


class PayoutStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"


class Payout(TimestampMixin):
    id = fields.UUIDField(pk=True, default=uuid6.uuid7)

    venue: ForeignKeyRelation["Venue"] = fields.ForeignKeyField(
        "models.Venue", related_name="payouts", on_delete=fields.RESTRICT
    )

    period_start = fields.DateField()
    period_end = fields.DateField()

    total_amount = fields.DecimalField(
        max_digits=10,
        decimal_places=2,
        description="The amount to be paid to the venue (The sum of all venue_amount)",
    )

    status = fields.CharEnumField(
        enum_type=PayoutStatus,
        default=PayoutStatus.PENDING,
        description="Transfer status of funds",
    )

    report_file_url = fields.CharField(
        max_length=512, null=True, description="Link to the generated PDF Report of the Agent in S3"
    )

    paid_at = fields.DatetimeField(
        null=True, description="The actual time of transfer to the IBAN of the venue"
    )

    class Meta:
        table = "payouts"
