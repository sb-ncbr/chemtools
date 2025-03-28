import logging

import aio_pika

from conf.settings import RabbitMQSettings

logger = logging.getLogger(__name__)


class MessageBrokerService:
    def __init__(self, rabbitmq_settings: RabbitMQSettings):
        self.rabbitmq_settings = rabbitmq_settings

    async def send_calculation_message(self, data: str, _queue: str):
        await self._send_message(
            rabbitmq_url=self.rabbitmq_settings.rabbitmq_url,
            queue_name=_queue,
            data=data,
        )

    async def _send_message(
        self,
        rabbitmq_url: str,
        queue_name: str,
        data: str,
    ):
        connection = await aio_pika.connect_robust(rabbitmq_url)
        async with connection:
            channel = await connection.channel()

            await channel.declare_queue(queue_name, durable=True)

            message = aio_pika.Message(
                body=data.encode(),
                content_type='application/json',
                delivery_mode=self.rabbitmq_settings.DELIVERY_MODE,
            )

            exchange = await channel.get_exchange(queue_name)
            await exchange.publish(message, routing_key=queue_name)

            logger.info(f"[x] Sent message to {queue_name}: {data}")
