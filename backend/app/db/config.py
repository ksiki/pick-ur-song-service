from typing import Any, Final

from app.core.config import settings

TORTOISE_ORM: Final[dict[str, Any]] = {
    "connections": {"default": settings.DATABASE_URL},
    "apps": {
        "models": {
            "models": [
                "app.modules.bars.models",
                "app.modules.orders.models",
                "app.modules.payments.models",
                "app.modules.music.models",
                "aerich.models",
            ],
            "default_connection": "default",
        },
    },
}
