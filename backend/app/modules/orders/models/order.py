from enum import Enum
from typing import TYPE_CHECKING

import uuid6
from app.db.models import TimestampMixin
from tortoise import fields
from tortoise.fields.relational import ForeignKeyRelation
from tortoise.indexes import Index

if TYPE_CHECKING:
    from app.modules.bars.models import Bar
    from app.modules.payments.models import Payout


class OrderStatus(str, Enum):
    PENDING_MODERATION = "pending_moderation"
    MODERATION_REJECTED = "moderation_rejected"
    PENDING_PAYMENT = "pending_payment"
    PAID = "paid"
    PAYMENT_FAILED = "payment_failed"
    PLAYED = "played"
    REFUNDED = "refunded"


class Order(TimestampMixin):
    id = fields.UUIDField(pk=True, default=uuid6.uuid7)

    bar: ForeignKeyRelation["Bar"] = fields.ForeignKeyField(
        "models.Bar", related_name="orders", on_delete=fields.RESTRICT
    )

    guest_session_id = fields.CharField(max_length=255, null=True)
    table_number = fields.CharField(max_length=20, null=True)

    track_id = fields.CharField(max_length=255)
    track_title = fields.CharField(max_length=255)
    track_artist = fields.CharField(max_length=255)
    track_artwork_url = fields.CharField(max_length=512, null=True)

    amount_total = fields.DecimalField(max_digits=10, decimal_places=2)
    service_commission = fields.DecimalField(
        max_digits=10, decimal_places=2, description="Our service's commission"
    )
    acquiring_fee = fields.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        description="Acquiring fees and other gateways",
    )
    bar_amount = fields.DecimalField(
        max_digits=10,
        decimal_places=2,
        description="Bar share (amount_total - service_commission - acquiring_fee)",
    )

    status = fields.CharEnumField(
        enum_type=OrderStatus, description="Current order status by life cycle"
    )
    reject_reason = fields.CharField(max_length=255, null=True)

    payout: ForeignKeyRelation["Payout"] | None = fields.ForeignKeyField(
        "models.Payout", related_name="orders", null=True, on_delete=fields.SET_NULL
    )

    class Meta:
        table = "orders"
        indexes = [
            Index(fields=("bar_id", "created_at")),
            Index(
                fields=("payout_id",),
                name="idx_orders_unpaid",
            ),
        ]
