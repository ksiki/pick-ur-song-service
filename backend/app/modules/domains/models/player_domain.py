from typing import TYPE_CHECKING

import uuid6
from app.db.models import TimestampMixin
from tortoise import fields

if TYPE_CHECKING:
    pass


class PlayerDomain(TimestampMixin):
    """Модель технического домена из пула для балансировки обращений к SoundCloud Widget API"""

    id = fields.UUIDField(pk=True, default=uuid6.uuid7)

    url = fields.CharField(
        max_length=255, unique=True, index=True, description="Уникальный URL технического домена"
    )

    max_capacity = fields.IntField(
        default=10, description="Максимальное количество заведений на один домен"
    )

    is_active = fields.BooleanField(
        default=True, description="Флаг активности домена (готов к приему баров)"
    )

    is_banned = fields.BooleanField(
        default=False, description="Флаг блокировки домена со стороны SoundCloud"
    )

    class Meta:
        table = "player_domains"
