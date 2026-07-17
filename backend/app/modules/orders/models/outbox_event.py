from enum import Enum
from typing import Any

import uuid6
from app.db.models import TimestampMixin
from tortoise import fields


class OutboxStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"


class OutboxEvent(TimestampMixin):
    id = fields.UUIDField(pk=True, default=uuid6.uuid7)

    event_type = fields.CharField(max_length=255, index=True)

    payload: dict[str, Any] = fields.JSONField()

    status = fields.CharEnumField(OutboxStatus, default=OutboxStatus.PENDING)

    processed_at = fields.DatetimeField(null=True)

    error_message = fields.TextField(null=True)

    class Meta:
        table = "outbox_events"
        indexes = (("status", "created_at"),)

    def __str__(self) -> str:
        return f"OutboxEvent({self.event_type}, status={self.status})"
