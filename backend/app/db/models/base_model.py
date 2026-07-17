from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tortoise.models import Model

    class BaseModel(Model):
        class Meta:
            abstract = True
else:
    from tortoise.models import Model as BaseModel  # noqa: F401
