import logging
import uuid
from typing import TYPE_CHECKING

from app.core.redis import redis_cache
from app.modules.venues.models import Venue

if TYPE_CHECKING:
    from pydantic import UUID4

logger = logging.getLogger(__name__)


class PlayerConnectionService:
    """
    Сервис управления сессиями WebSocket-плееров через Redi
    """

    @staticmethod
    def _sessions_key(venue_id: "UUID4 | str") -> str:
        return f"venue:{venue_id}:ws_sessions"

    @classmethod
    async def register_connection(cls, venue_id: "UUID4 | str") -> str:
        session_id = str(uuid.uuid4())
        key = cls._sessions_key(venue_id)

        await redis_cache.safe_client.sadd(key, session_id)
        await Venue.filter(id=venue_id).update(player_is_active=True)

        logger.info(f"Player for venue {venue_id} connected. Assigned session: {session_id}")
        return session_id

    @classmethod
    async def is_session_valid(cls, venue_id: "UUID4 | str", session_id: str) -> bool:
        key = cls._sessions_key(venue_id)
        result = await redis_cache.safe_client.sismember(key, session_id)
        return bool(result)

    @classmethod
    async def handle_disconnect(cls, venue_id: "UUID4 | str", session_id: str) -> None:
        key = cls._sessions_key(venue_id)

        await redis_cache.safe_client.srem(key, session_id)
        active_sessions_count = await redis_cache.safe_client.scard(key)

        if active_sessions_count == 0:
            await Venue.filter(id=venue_id).update(player_is_active=False)
            logger.info(f"All players for venue {venue_id} disconnected. Marked inactive.")
        else:
            logger.debug(
                f"""Session {session_id} for venue {venue_id} terminated.
                {active_sessions_count} devices still online."""
            )
