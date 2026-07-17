from typing import TYPE_CHECKING

import uuid6
from app.db.models import TimestampMixin
from tortoise import fields

if TYPE_CHECKING:
    pass


class Account(TimestampMixin):
    """Модель бизнес-аккаунта (владельца сети заведений)."""

    id = fields.UUIDField(pk=True, default=uuid6.uuid7)

    email = fields.CharField(max_length=255, unique=True, index=True)
    password_hash = fields.CharField(max_length=255)
    is_email_verified = fields.BooleanField(default=False)

    legal_name = fields.CharField(
        max_length=255, null=True, description="Юридическое лицо (ИП / ООО)"
    )
    unp = fields.CharField(max_length=9, null=True, description="УНП")
    iban = fields.CharField(max_length=28, null=True, description="Расчетный счет (IBAN)")

    offer_accepted_at = fields.DatetimeField(null=True)
    offer_accepted_ip = fields.CharField(max_length=45, null=True)
    is_active = fields.BooleanField(
        default=False, description="Пройден ли юридический онбординг аккаунтом"
    )

    # Reverse relations (для тайп-хинтинга Tortoise):
    # bars: fields.ReverseRelation["Bar"]
    # sessions: fields.ReverseRelation["RefreshSession"]

    class Meta:
        table = "accounts"
