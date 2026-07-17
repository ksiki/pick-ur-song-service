import logging

from faststream.rabbit import RabbitBroker

from app.core.config import settings

logger = logging.getLogger(__name__)

broker = RabbitBroker(settings.RABBITMQ_URL)
