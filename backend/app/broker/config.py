import logging

from faststream import FastStream
from tortoise import Tortoise

from app.broker.client import broker
from app.db.config import TORTOISE_ORM
from app.modules.auth.tasks import auth_router
from app.modules.domains.tasks import domains_router
from app.modules.orders.tasks import orders_router
from app.modules.player.tasks import player_router

logger = logging.getLogger(__name__)

stream_app = FastStream(broker)
broker.include_router(orders_router)
broker.include_router(auth_router)
broker.include_router(domains_router)
broker.include_router(player_router)


@stream_app.on_startup
async def startup() -> None:
    """
    Выполняется один раз при запуске процесса воркера FastStream.
    Обязательно инициализируем пул соединений с БД, так как консьюмеры
    будут писать статусы заказов (Ledger).
    """
    await Tortoise.init(config=TORTOISE_ORM)
    logger.info("FastStream Worker: DB connected via Tortoise ORM")


@stream_app.on_shutdown
async def shutdown() -> None:
    """Выполняется при остановке воркера"""
    await Tortoise.close_connections()
    logger.info("FastStream Worker: DB connections closed")
