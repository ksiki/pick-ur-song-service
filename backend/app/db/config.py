from typing import Any, Final

from app.core.config import settings

TORTOISE_ORM: Final[dict[str, Any]] = {
    "connections": {"default": settings.DATABASE_URL},
    "apps": {
        "models": {
            "models": [
                "app.modules.auth.models",
                "app.modules.venues.models",
                "app.modules.orders.models",
                "app.modules.payments.models",
                "app.modules.music.models",
                "app.modules.accounts.models",
                "app.modules.domains.models",
                "app.modules.soundcloud.models",
                "aerich.models",
            ],
            "default_connection": "default",
        },
    },
}
