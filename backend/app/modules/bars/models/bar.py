import uuid6
from app.db.models import TimestampMixin
from tortoise import fields


class Bar(TimestampMixin):
    id = fields.UUIDField(pk=True, default=uuid6.uuid7)

    login = fields.CharField(max_length=100, unique=True)
    password_hash = fields.CharField(max_length=255)
    admin_passcode_hash = fields.CharField(
        max_length=255, null=True, description="Hash of the passphrase for access to the admin area"
    )

    name = fields.CharField(max_length=255)
    legal_name = fields.CharField(max_length=255)
    unp = fields.CharField(max_length=9)
    iban = fields.CharField(max_length=28)

    offer_accepted_at = fields.DatetimeField()
    offer_accepted_ip = fields.CharField(max_length=45)

    is_active = fields.BooleanField(default=True)

    class Meta:
        table = "bars"
