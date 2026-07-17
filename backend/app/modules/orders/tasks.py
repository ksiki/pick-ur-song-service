import logging
from typing import Any
from uuid import UUID

from app.modules.music.schemas import TrackSourceType
from app.modules.music.services import QueueService
from app.modules.orders.models import Order, OrderStatus
from faststream.rabbit import RabbitRouter
from tortoise.exceptions import DoesNotExist

logger = logging.getLogger(__name__)

orders_router = RabbitRouter()


@orders_router.subscriber("order_paid_queue")
async def process_paid_order(payload: dict[str, Any]) -> None:
    """
    Обрабатывает событие успешной оплаты заказа.
    1. Обновляет статус в БД (PostgreSQL).
    2. Добавляет трек в живую очередь (Redis).
    """
    order_id_str = payload.get("order_id")
    if not order_id_str:
        return

    try:
        order_id = UUID(order_id_str)
        order = await Order.get(id=order_id)
    except (ValueError, DoesNotExist):
        logger.error(f"Order {order_id_str} not found during payment processing.")
        return

    if order.status != OrderStatus.PENDING_PAYMENT:
        logger.warning(f"Order {order.id} is already processed (Status: {order.status})")
        return

    order.status = OrderStatus.PAID
    await order.save()
    logger.info(f"Order {order.id} marked as PAID")

    # 2. Определяем тип трека (VIP или обычный)
    # В реальной системе здесь будет проверка: order.amount_total == settings.track_price_no_queue
    # Для примера предположим, что это обычный заказ:
    source_type = TrackSourceType.ORDER

    track_data = {
        "track_id": order.track_id,
        "track_url": order.track_url,
        "title": order.track_title,
        "artist": order.track_artist,
        "artwork_url": order.track_artwork_url,
        "duration_ms": order.track_duration_ms,
        "source_type": source_type,
        "order_id": order.id,
    }

    try:
        await QueueService.add_track(venue_id=order.venue.id, track_data=track_data)
        logger.info(f"Track {order.track_id} added to live queue for bar {order.venue.id}")
    except Exception as e:
        logger.error(f"Failed to add track to queue for order {order.id}: {e}")


@orders_router.subscriber("order_played_queue")
async def process_played_order(payload: dict[str, Any]) -> None:
    """
    Переводит статус заказа в PLAYED после фактического воспроизведения в баре.
    """
    order_id_str = payload.get("order_id")
    if not order_id_str:
        return

    try:
        order = await Order.get(id=UUID(order_id_str))
        if order.status == OrderStatus.PAID:
            order.status = OrderStatus.PLAYED
            await order.save(update_fields=["status"])
            logger.info(f"Order {order.id} successfully marked as PLAYED")
    except DoesNotExist:
        logger.error(f"Order {order_id_str} not found for PLAYED status update")
