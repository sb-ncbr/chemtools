import logging

import aio_pika
from aio_pika.patterns import JsonMaster

from conf.settings import RabbitMQSettings

logger = logging.getLogger(__name__)


class MessageBrokerService:
    def __init__(self, rabbitmq_settings: RabbitMQSettings):
        self.rabbitmq_settings = rabbitmq_settings

    async def send_calculation_message(self, data: str, _queue: str):
        await self._send_message(
            queue_name=_queue,
            data=data,
        )

    async def _send_message(self, queue_name: str, data: str, **options) -> None:
        connection = await aio_pika.connect_robust(self.rabbitmq_settings.rabbitmq_url)
        async with connection:
            channel = await connection.channel()
            master = JsonMaster(channel)

            await master.create_task(channel_name=queue_name, kwargs=data, **options)
            logger.info(f"[x] Message sent to {queue_name}: {data}")
