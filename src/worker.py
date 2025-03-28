import asyncio
import logging.config

import aio_pika
from dependency_injector.wiring import Provide, inject

from conf.settings import PostgresSettings, RabbitMQSettings, WorkerSettings
from containers import WorkerContainer
from db.database import DatabaseSessionManager
from services.message_broker_service import JsonMaster
from services.worker_service import WorkerService
from utils import get_project_version, init_logging, init_worker_di

logger = logging.getLogger("worker")


@inject
async def init_worker(
    worker_service: WorkerService = Provide[WorkerContainer.worker_service],
    worker_settings: WorkerSettings = Provide[WorkerContainer.worker_settings],
    rabbitmq_settings: RabbitMQSettings = Provide[WorkerContainer.rabbitmq_settings],
    db_settings: PostgresSettings = Provide[WorkerContainer.postgres_settings],
    session_manager: DatabaseSessionManager = Provide[WorkerContainer.session_manager],
) -> aio_pika.robust_connection.AbstractRobustConnection:
    init_logging(worker_settings)
    session_manager.init(db_settings.postgres_url)

    print(f"Starting chemtools-worker (using chemtools-api-v{get_project_version()})")
    connection = await aio_pika.connect_robust(rabbitmq_settings.rabbitmq_url)
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=1)

    master = JsonMaster(channel)
    await asyncio.gather(
        master.create_worker("free_queue", worker_service.run_calculation_async, durable=True),
        master.create_worker("pipeline_queue", worker_service.run_calculation_async, durable=True),
    )
    logger.info("Connected to RabbitMQ")
    return connection


async def run_worker_mainloop() -> None:
    connection = await init_worker()
    try:
        await asyncio.Future()
    except asyncio.exceptions.CancelledError:
        logger.info("Shutting down worker...")
    finally:
        await connection.close()


if __name__ == "__main__":
    init_worker_di()
    asyncio.run(run_worker_mainloop())
