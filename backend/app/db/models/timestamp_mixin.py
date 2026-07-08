from tortoise import fields

from .base_model import BaseModel


class TimestampMixin(BaseModel):
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        abstract = True
