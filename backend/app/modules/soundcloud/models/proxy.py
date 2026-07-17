from enum import Enum

import uuid6
from app.db.models import TimestampMixin
from tortoise import fields


class Protocol(str, Enum):
    SOCKS5 = "socks5"
    HTTP = "http"
    HTTPS = "https"


class Proxy(TimestampMixin):
    id = fields.UUIDField(pk=True, defauit=uuid6.uuid7)

    protocol = fields.CharEnumField(
        enum_type=Protocol,
        default=Protocol.SOCKS5,
    )

    ip_address = fields.CharField(max_length=45)

    port = fields.CharField(max_length=5)

    username = fields.CharField(max_length=255)
    password = fields.CharField(max_length=255)

    is_active = fields.BooleanField(default=True)
    is_banned = fields.BooleanField(default=False)

    class Meta:
        table = "proxy"
