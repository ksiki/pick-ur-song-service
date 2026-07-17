from typing import TYPE_CHECKING

import uuid6
from app.db.models import TimestampMixin
from tortoise import fields
from tortoise.fields.relational import ForeignKeyRelation

if TYPE_CHECKING:
    from app.modules.accounts.models import Account
    from app.modules.domains.models import PlayerDomain


class Venue(TimestampMixin):
    """Модель конкретного заведения (физической точки)."""

    id = fields.UUIDField(pk=True, default=uuid6.uuid7)

    account: ForeignKeyRelation["Account"] = fields.ForeignKeyField(
        "models.Account",
        related_name="venues",
        on_delete=fields.CASCADE,
        description="Владелец заведения (бизнес-аккаунт)",
    )

    name = fields.CharField(max_length=255, description="Коммерческое название заведения")
    number = fields.CharField(max_length=15, description="Контактный телефон бара")

    address = fields.CharField(
        max_length=255, description="Адрес вида: Беларусть, Гомель, Советская, 34"
    )

    admin_passcode_hash = fields.CharField(
        max_length=255,
        null=True,
        description="Хеш кодовой фразы для админской зоны конкретного бара",
    )

    assigned_domain: ForeignKeyRelation["PlayerDomain"] | None = fields.ForeignKeyField(
        "models.PlayerDomain",
        related_name="venues",
        null=True,
        on_delete=fields.SET_NULL,
        description="Назначенный технический домен для SoundCloud плеера",
    )

    player_is_active = fields.BooleanField(
        default=False,
        description="""Нужно для того,
        что бы нельзя было включать музыку в одном бару сразу с нескольких устройств""",
    )

    is_active = fields.BooleanField(
        default=True,
        description="Активно ли конкретное заведение (можно выключить точку не удаляя аккаунт)",
    )

    class Meta:
        table = "venues"
