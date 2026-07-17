import json
import uuid
from typing import Any

from app.broker.publisher import EventPublisher
from app.broker.schemas import PlayTrackCommand
from app.core.redis import redis_cache
from app.modules.music.schemas import QueueItem, TrackSourceType
from fastapi import HTTPException, status
from pydantic import UUID4


class QueueService:
    """
    Управляет живой очередью воспроизведения бара в Redis.
    Обеспечивает бизнес-правила: строгую приоритетность заказов, VIP-перескок, защиту от дублей.
    """

    @staticmethod
    def _playing_key(venue_id: UUID4) -> str:
        return f"venue:{venue_id}:currently_playing"

    @staticmethod
    def _queue_key(venue_id: UUID4) -> str:
        return f"venue:{venue_id}:live_queue"

    @classmethod
    async def _save_queue(cls, venue_id: UUID4, items: list[QueueItem]) -> None:
        """Сохраняет очередь обратно в Redis"""
        data = json.dumps([item.model_dump(mode="json") for item in items])
        await redis_cache.safe_client.set(cls._queue_key(venue_id), data)

    @classmethod
    async def get_queue(cls, venue_id: UUID4) -> list[QueueItem]:
        """Получает текущую очередь из Redis"""
        data = await redis_cache.safe_client.get(cls._queue_key(venue_id))
        if not data:
            return []
        items_dict = json.loads(data)
        return [QueueItem(**item) for item in items_dict]

    @classmethod
    async def get_currently_playing(cls, venue_id: UUID4) -> QueueItem | None:
        """Возвращает трек, который играет прямо сейчас (или None)"""
        data = await redis_cache.safe_client.get(cls._playing_key(venue_id))
        if data:
            return QueueItem(**json.loads(data))
        return None

    @classmethod
    async def add_track(cls, venue_id: UUID4, track_data: dict[str, Any]) -> QueueItem:
        """
        Добавляет трек в очередь с соблюдением приоритета:
        VIP_ORDER -> ORDER -> BACKGROUND.
        Текущий играющий трек при этом никогда не прерывается.
        """
        current_queue = await cls.get_queue(venue_id)

        currently_playing_data = await redis_cache.safe_client.get(cls._playing_key(venue_id))
        playing_track = (
            QueueItem(**json.loads(currently_playing_data)) if currently_playing_data else None
        )

        new_item = QueueItem(
            queue_id=str(uuid.uuid4()),
            **track_data,
        )

        insert_index = len(current_queue)

        if new_item.source_type == TrackSourceType.VIP_ORDER:
            for i, item in enumerate(current_queue):
                if item.source_type != TrackSourceType.VIP_ORDER:
                    insert_index = i
                    break
        elif new_item.source_type == TrackSourceType.ORDER:
            for i, item in enumerate(current_queue):
                if item.source_type == TrackSourceType.BACKGROUND:
                    insert_index = i
                    break

        preceding_track = current_queue[insert_index - 1] if insert_index > 0 else playing_track

        if preceding_track and preceding_track.track_id == new_item.track_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Этот трек уже находится следующим в очереди. Выберите другой трек.",
            )

        current_queue.insert(insert_index, new_item)
        await cls._save_queue(venue_id, current_queue)

        if not playing_track and len(current_queue) == 1:
            await cls.trigger_playback(venue_id)

        return new_item

    @classmethod
    async def add_track_next(cls, venue_id: UUID4, track_data: dict[str, Any]) -> QueueItem:
        """
        Принудительно добавляет трек следующим в очередь (на позицию 0).
        Игнорирует стандартную приоритизацию.
        """
        current_queue = await cls.get_queue(venue_id)

        currently_playing_data = await redis_cache.safe_client.get(cls._playing_key(venue_id))
        playing_track = (
            QueueItem(**json.loads(currently_playing_data)) if currently_playing_data else None
        )

        new_item = QueueItem(
            queue_id=str(uuid.uuid4()),
            **track_data,
        )

        if playing_track and playing_track.track_id == new_item.track_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Этот трек уже играет прямо сейчас. Выберите другой трек.",
            )

        current_queue.insert(0, new_item)
        await cls._save_queue(venue_id, current_queue)

        if not playing_track:
            await cls.trigger_playback(venue_id)

        return new_item

    @classmethod
    async def add_playlist(cls, venue_id: UUID4, items: list[QueueItem]) -> None:
        """
        Массовое добавление списка треков (плейлиста) в живую очередь.
        Очищает очередь от старых фоновых треков (BACKGROUND), оставляя только заказы.
        """
        if not items:
            return

        current_queue = await cls.get_queue(venue_id)

        filtered_queue = [
            item
            for item in current_queue
            if item.source_type in (TrackSourceType.ORDER, TrackSourceType.VIP_ORDER)
        ]

        filtered_queue.extend(items)
        await cls._save_queue(venue_id, filtered_queue)

        currently_playing_data = await redis_cache.safe_client.get(cls._playing_key(venue_id))
        playing_track = (
            QueueItem(**json.loads(currently_playing_data)) if currently_playing_data else None
        )

        if not playing_track:
            await cls.trigger_playback(venue_id)

    @classmethod
    async def apply_drag_and_drop(cls, venue_id: UUID4, new_order_ids: list[str]) -> None:
        """
        Применяет новый порядок элементов очереди от админ-панели (фронтенда).
        """
        current_queue = await cls.get_queue(venue_id)

        current_ids = {item.queue_id for item in current_queue}
        if set(new_order_ids) != current_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Queue state mismatch. Please refresh and try again.",
            )

        queue_map = {item.queue_id: item for item in current_queue}
        reordered_queue = [queue_map[qid] for qid in new_order_ids]

        await cls._save_queue(venue_id, reordered_queue)

    @classmethod
    async def pop_next_track(cls, venue_id: UUID4) -> QueueItem | None:
        """
        Извлекает следующий трек из очереди, переводит его в статус playing
        и удаляет из списка ожидающих.
        """
        current_queue = await cls.get_queue(venue_id)
        if not current_queue:
            await redis_cache.safe_client.delete(cls._playing_key(venue_id))
            return None

        next_track = current_queue.pop(0)

        await cls._save_queue(venue_id, current_queue)
        await redis_cache.safe_client.set(
            cls._playing_key(venue_id), json.dumps(next_track.model_dump(mode="json"))
        )

        return next_track

    @classmethod
    async def trigger_playback(cls, venue_id: UUID4) -> None:
        """
        Извлекает первый трек из очереди и отправляет команду плеера в RabbitMQ.
        """
        next_track = await cls.pop_next_track(venue_id)
        if not next_track:
            return

        command = PlayTrackCommand(
            venue_id=venue_id,
            order_id=next_track.order_id,
            track_id=next_track.track_id,
            track_url=next_track.track_url,
            title=next_track.title,
            artist=next_track.artist,
            artwork_url=next_track.artwork_url,
            duration_ms=next_track.duration_ms,
            source_type=next_track.source_type,
        )

        await EventPublisher.publish_play_command(command)
