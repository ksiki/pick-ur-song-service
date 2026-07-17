import logging
from typing import TYPE_CHECKING, Any, Final

from fastapi import WebSocket

if TYPE_CHECKING:
    from pydantic import UUID4

logger: Final[logging.Logger] = logging.getLogger(__name__)


class PlayerWebSocketManager:
    """
    Локальный менеджер WebSocket-соединений.
    Теперь поддерживает несколько подключений (устройств) для одного заведения.
    """

    _active_connections: dict[str, set[WebSocket]] = {}

    @classmethod
    async def connect(cls, bar_id: "UUID4 | str", websocket: WebSocket) -> None:
        """
        Принимает WebSocket соединение и добавляет его в множество сессий бара.
        """
        await websocket.accept()
        bar_id_str = str(bar_id)

        if bar_id_str not in cls._active_connections:
            cls._active_connections[bar_id_str] = set()

        cls._active_connections[bar_id_str].add(websocket)
        logger.debug(
            f"""Local WS memory: accepted connection for bar {bar_id_str}.
            Total: {len(cls._active_connections[bar_id_str])}"""
        )

    @classmethod
    def disconnect(cls, bar_id: "UUID4 | str", websocket: WebSocket) -> None:
        """
        Удаляет конкретный сокет из локальной памяти при дисконнекте.
        Если множество становится пустым, удаляет ключ бара.
        """
        bar_id_str = str(bar_id)
        if bar_id_str in cls._active_connections:
            if websocket in cls._active_connections[bar_id_str]:
                cls._active_connections[bar_id_str].remove(websocket)

            if not cls._active_connections[bar_id_str]:
                del cls._active_connections[bar_id_str]
                logger.debug(f"Local WS memory: all connections removed for bar {bar_id_str}")
            else:
                logger.debug(
                    f"""Local WS memory: connection removed for bar {bar_id_str}.
                    Remaining: {len(cls._active_connections[bar_id_str])}"""
                )

    @classmethod
    async def send_to_bar(cls, bar_id: "UUID4 | str", message: dict[str, Any]) -> bool:
        """
        Отправляет JSON-сообщение ВСЕМ подключенным устройствам конкретного бара.
        """
        bar_id_str = str(bar_id)
        websockets = cls._active_connections.get(bar_id_str, set())

        if not websockets:
            return False

        dead_sockets = set()
        sent_at_least_one = False

        for ws in websockets:
            try:
                await ws.send_json(message)
                sent_at_least_one = True
            except Exception as e:
                logger.error(f"Error sending message to bar {bar_id_str}: {e}")
                dead_sockets.add(ws)

        for dead_ws in dead_sockets:
            cls.disconnect(bar_id, dead_ws)

        return sent_at_least_one

    @classmethod
    def get_connected_bars(cls) -> list[str]:
        return list(cls._active_connections.keys())
