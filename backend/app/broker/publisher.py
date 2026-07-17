import logging
from datetime import UTC, datetime
from uuid import UUID

from pydantic import UUID4

from app.broker.client import broker
from app.broker.schemas import PlayTrackCommand

logger = logging.getLogger(__name__)


class EventPublisher:
    """
    Слой абстракции для публикации событий в RabbitMQ.
    Инкапсулирует логику маршрутизации и обменов.
    """

    @staticmethod
    async def publish_play_command(command: PlayTrackCommand) -> None:
        """
        Отправляет команду на воспроизведение трека в Fanout-обменник.
        Сообщение будет доставлено всем запущенным воркерам FastAPI.
        """
        await broker.publish(
            message=command,
            exchange="player_commands_exchange",
        )
        logger.debug(f"Published PlayTrackCommand for venue {command.venue_id}")

    @staticmethod
    async def publish_order_paid(order_id: str) -> None:
        """
        Уведомление об успешной оплате (вызывается из REST API вебхука эквайринга)
        """
        await broker.publish(message={"order_id": order_id}, queue="order_paid_queue")

    @staticmethod
    async def publish_playlist_sync(venue_id: UUID4, playlist_id: UUID4) -> None:
        """
        Уведомляет плеер бара о том, что фоновый плейлист обновился.
        """
        await broker.publish(
            message={"bar_id": str(venue_id), "playlist_id": str(playlist_id)},
            exchange="player_commands_exchange",
        )
        logger.debug(f"Published Playlist Sync command for venue {venue_id}")

    @staticmethod
    async def publish_order_played(
        order_id: UUID, track_id: int, was_skipped: bool = False
    ) -> None:
        """
        Уведомляет систему, что заказ успешно воспроизведен (или пропущен).
        """
        await broker.publish(
            message={
                "order_id": str(order_id),
                "track_id": track_id,
                "was_skipped": was_skipped,
            },
            queue="order_played_queue",
        )
        logger.debug(f"Published Order Played command for order {order_id}")

    @staticmethod
    async def publish_emergency_key_parsing() -> None:
        """
        Экстренно уведомляет систему о нехватке ключей SoundCloud.
        Воркер, слушающий эту очередь, должен запустить парсинг новых ключей.
        """
        await broker.publish(
            message={"alert": "KEYS_EXHAUSTED", "timestamp": str(datetime.now(UTC))},
            queue="emergency_key_parsing_queue",
        )
        logger.warning("Published EMERGENCY EVENT: Key parsing required!")
