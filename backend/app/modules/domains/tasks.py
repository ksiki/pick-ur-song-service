import logging

from app.broker.client import broker
from app.modules.domains.models import PlayerDomain
from app.modules.venues.models import Venue
from faststream.rabbit import RabbitRouter

logger = logging.getLogger(__name__)

domains_router = RabbitRouter()


@domains_router.subscriber("domain_ban_queue")
async def ban_domain_task(domain_id: str) -> None:
    """
    Аварийная отвязка домена (FastStream Worker).
    Блокирует домен и рассылает WebSocket-события пострадавшим барам.
    """
    domain: PlayerDomain | None = await PlayerDomain.get_or_none(id=domain_id)
    if not domain or domain.is_banned:
        return

    domain.is_banned = True
    domain.is_active = False
    await domain.save(update_fields=["is_banned", "is_active", "updated_at"])

    affected_venues = await Venue.filter(assigned_domain=domain).all()

    for venue in affected_venues:
        venue.assigned_domain = None
        await venue.save(update_fields=["assigned_domain_id", "updated_at"])

        await broker.publish(
            message={"action": "force_reconnect"},
            queue=f"ws_venue_{venue.id}",
        )
        logger.info(f"[УСПЕХ] Отправлен force_reconnect заведению {venue.id}")


@domains_router.subscriber("check_domain_capacity_queue")
async def check_domain_capacity() -> None:
    """
    Воркер алертов.
    Ожидается, что внешний планировщик (Taskiq, Celery Beat или cron-скрипт)
    будет публиковать пустое сообщение в эту очередь раз в час.
    """
    active_domains = await PlayerDomain.filter(is_active=True, is_banned=False).all()

    total_capacity = 0
    total_venues_assigned = 0

    for domain in active_domains:
        total_capacity += domain.max_capacity
        current_load = await domain.venues.all().count()  # type: ignore[attr-defined]
        total_venues_assigned += current_load

    free_slots = total_capacity - total_venues_assigned

    if free_slots < 5:
        # TODO: Заменить на реальную интеграцию с Telegram API
        logger.critical(
            f"""[АЛЕРТ] Заканчивается пул доменов! Осталось {free_slots} слотов.client.py
            Срочно добавьте новые!"""
        )
