import logging
from typing import Any, Final

from app.modules.player.services import PlayerWebSocketManager
from faststream.rabbit import ExchangeType, RabbitExchange, RabbitQueue, RabbitRouter

logger: Final[logging.Logger] = logging.getLogger(__name__)

player_router: Final[RabbitRouter] = RabbitRouter()

player_commands_exchange: Final[RabbitExchange] = RabbitExchange(
    "player_commands_exchange",
    type=ExchangeType.FANOUT,
    durable=True,
)


@player_router.subscriber(RabbitQueue(""), exchange=player_commands_exchange)
async def process_player_broadcast(payload: dict[str, Any]) -> None:
    """
    Принимает широковещательные команды плеера из RabbitMQ (Fanout).

    Поскольку обменник работает в режиме Fanout, это событие получат все запущенные воркеры.
    Каждый воркер проверяет, находится ли активное WebSocket-соединение этого бара
    на его инстансе. Если да — отправляет команду на фронтенд плеера.
    """
    venue_id = payload.get("venue_id")
    if not venue_id:
        logger.warning("Received player broadcast command without 'venue_id'")
        return

    was_sent = await PlayerWebSocketManager.send_to_bar(venue_id, payload)

    if was_sent:
        logger.info(f"Successfully forwarded broadcast command to player WS for bar {venue_id}")
    else:
        logger.debug(
            f"Broadcast command ignored: bar {venue_id} is not connected to this worker instance"
        )
