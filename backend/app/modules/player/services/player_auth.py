import jwt
from app.core.config import settings
from app.modules.venues.models import Venue


class PlayerAuthService:
    """Вспомогательный сервис для аутентификации WebSocket соединений"""

    @staticmethod
    async def get_venue_from_token(token: str) -> Venue | None:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

            if payload.get("type") != "player_iframe":
                return None

            venue_id_str = payload.get("sub")
            if not venue_id_str:
                return None

            venue = await Venue.get_or_none(id=venue_id_str)
            if venue and venue.is_active:
                return venue

        except (jwt.InvalidTokenError, jwt.ExpiredSignatureError):
            return None
        return None
