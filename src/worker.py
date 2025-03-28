import asyncio
import json
import logging.config

import aio_pika
from dependency_injector.wiring import Provide, inject

from conf.settings import PostgresSettings, RabbitMQSettings, WorkerSettings
from containers import WorkerContainer
from db.database import DatabaseSessionManager
from services.worker_service import WorkerService
from utils import get_project_version, init_logging, init_worker_di

logger = logging.getLogger("worker")


@inject
async def init_worker(
    worker_settings: WorkerSettings = Provide[WorkerContainer.worker_settings],
    rabbitmq_settings: RabbitMQSettings = Provide[WorkerContainer.rabbitmq_settings],
    db_settings: PostgresSettings = Provide[WorkerContainer.postgres_settings],
    session_manager: DatabaseSessionManager = Provide[WorkerContainer.session_manager],
):
    init_logging(worker_settings)
    session_manager.init(db_settings.postgres_url)

    print(f"Starting chemtools-worker (using chemtools-api-v{get_project_version()})")
    connection = await aio_pika.connect_robust(rabbitmq_settings.rabbitmq_url)
    return connection


@inject
async def run_calculation_task(
    data: dict, worker_service: WorkerService = Provide[WorkerContainer.worker_service]
) -> None:
    logger.info(f"Received message: {data}")
    await worker_service.run_calculation_async(data)


@inject
async def consume_queue(
    queue_name: str,
    channel: aio_pika.Channel,
    worker_service: WorkerService = Provide[WorkerContainer.worker_service],
):
    queue = await channel.declare_queue(queue_name, durable=True)
    logger.info(f"Listening to queue: {queue_name}")

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                try:
                    data = json.loads(message.body.decode())
                    await run_calculation_task(data, worker_service=worker_service)
                except Exception as e:
                    logger.error(f"Error processing message: {e}")


async def main():
    connection = await init_worker()
    channel = await connection.channel()
    logger.info("Connected to RabbitMQ")

    await channel.set_qos(prefetch_count=1)

    await asyncio.gather(
        consume_queue("free_queue", channel),
        consume_queue("pipeline_queue", channel),
    )


init_worker_di()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Shutting down worker...")
