from typing import TYPE_CHECKING

import uuid6
from app.db.models import TimestampMixin
from tortoise import fields
from tortoise.fields.relational import ForeignKeyRelation

if TYPE_CHECKING:
    from app.modules.accounts.models import Account


class RefreshSession(TimestampMixin):
    """Модель активной сессии авторизации аккаунта (Token Rotation)."""

    id = fields.UUIDField(pk=True, default=uuid6.uuid7)

    account: ForeignKeyRelation["Account"] = fields.ForeignKeyField(
        "models.Account",
        related_name="sessions",
        on_delete=fields.CASCADE,
        description="Аккаунт владельца, которому принадлежит сессия",
    )

    refresh_token_jti = fields.CharField(max_length=36, unique=True, index=True)

    user_agent = fields.CharField(
        max_length=512, description="Браузер и ОС (например, Chrome on Linux)"
    )
    ip_address = fields.CharField(max_length=45, description="IP адрес входа")

    expires_at = fields.DatetimeField(description="Время, когда сессия протухнет")

    class Meta:
        table = "refresh_sessions"
