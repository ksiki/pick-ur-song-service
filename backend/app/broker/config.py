from typing import Any, Final

from app.core.config import settings
from app.db.config import TORTOISE_ORM
from taskiq import TaskiqEvents, TaskiqState
from taskiq_aio_pika import AioPikaBroker
from taskiq_redis import RedisAsyncResultBackend
from tortoise import Tortoise

result_backend: Final = RedisAsyncResultBackend[Any](
    redis_url=settings.REDIS_URL,
)

broker: Final[AioPikaBroker] = AioPikaBroker(
    url=settings.RABBITMQ_URL,
).with_result_backend(result_backend)


@broker.on_event(TaskiqEvents.WORKER_STARTUP)
async def startup(state: TaskiqState) -> None:
    """Выполняется один раз при запуске процесса воркера"""
    await Tortoise.init(config=TORTOISE_ORM)
    print("Taskiq Worker: DB connected")


@broker.on_event(TaskiqEvents.WORKER_SHUTDOWN)
async def shutdown(state: TaskiqState) -> None:
    """Выполняется при остановке воркера"""
    await Tortoise.close_connections()
    print("Taskiq Worker: Connection since DB be closed")
