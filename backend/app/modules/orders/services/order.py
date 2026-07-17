import logging
from typing import Any
from uuid import UUID

from app.core.exceptions import OrderValidationException
from app.modules.music.services import QueueService
from app.modules.orders.models import Order, OrderStatus
from app.modules.venues.models import VenueSettings

logger = logging.getLogger(__name__)


class OrderService:
    """
    Сервис управления жизненным циклом заказов
    """

    @staticmethod
    async def pre_validate_track(venue_id: UUID, track_id: str) -> VenueSettings:
        """
        Проверяет, можно ли заказать данный трек в конкретном заведении.
        Возвращает настройки бара (VenueSettings), чтобы сразу использовать актуальную цену.
        """
        settings = await VenueSettings.get(venue_id=venue_id)

        current_queue = await QueueService.get_queue(venue_id)
        if any(str(item.track_id) == track_id for item in current_queue):
            raise OrderValidationException("Этот трек уже находится в очереди воспроизведения.")

        playing_track = await QueueService.get_currently_playing(venue_id)
        if playing_track and str(playing_track.track_id) == track_id:
            raise OrderValidationException("Этот трек играет прямо сейчас.")

        return settings

    @classmethod
    async def create_pending_order(
        cls, venue_id: UUID, guest_session_id: str, track_data: dict[str, Any], is_vip: bool = False
    ) -> Order:
        """
        Создает заказ в БД в статусе PENDING_PAYMENT.
        Вызывается, когда гость нажал "Заказать" и прошел валидацию.
        """
        settings = await cls.pre_validate_track(
            venue_id=venue_id,
            track_id=track_data["track_id"],
        )

        # Рассчитываем итоговую стоимость
        base_price = settings.track_price_no_queue if is_vip else settings.track_price

        # Расчет комиссий (бизнес-логика)
        service_commission = base_price * (settings.commission_fee_percent / 100)
        venue_amount = base_price - service_commission

        # Создаем запись через Tortoise ORM
        order = await Order.create(
            venue_id=venue_id,
            guest_session_id=guest_session_id,
            track_id=track_data["track_id"],
            track_title=track_data["title"],
            track_artist=track_data["artist"],
            track_artwork_url=track_data.get("artwork_url"),
            amount_total=base_price,
            service_commission=service_commission,
            venue_amount=venue_amount,
            status=OrderStatus.PENDING_PAYMENT,
            # Дополнительные поля, например acquiring_fee, заполнятся позже вебхуком эквайринга
        )

        logger.info(f"Created PENDING order {order.id} for venue {venue_id} (VIP: {is_vip})")
        return order
