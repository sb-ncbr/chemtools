import asyncio
import logging.config

from celery import Celery
from dependency_injector.wiring import Provide, inject

from conf.settings import PostgresSettings, RabbitMQSettings, WorkerSettings
from containers import WorkerContainer
from db.database import DatabaseSessionManager
from services.worker_service import WorkerService
from utils import get_project_version, init_logging, init_worker_di

logger = logging.getLogger(__name__)


@inject
def init_worker(
    worker_settings: WorkerSettings = Provide[WorkerContainer.worker_settings],
    rabbitmq_settings: RabbitMQSettings = Provide[WorkerContainer.rabbitmq_settings],
    db_settings: PostgresSettings = Provide[WorkerContainer.postgres_settings],
    session_manager: DatabaseSessionManager = Provide[WorkerContainer.session_manager],
) -> Celery:
    init_logging(worker_settings)
    session_manager.init(db_settings.postgres_url)

    print(f"Starting chemtools-worker (using chemtools-api-v{get_project_version()})")
    celery_worker = Celery(
        "worker",
        broker=rabbitmq_settings.rabbitmq_url,
        task_queues={
            "bunny_tube": {
                "exchange": "bunny_tube",
                "routing_key": "bunny_tube",
                "queue_arguments": {"x-max-priority": 2},
            }
        },
        broker_connection_retry_on_startup=True,
        worker_prefetch_multiplier=1,
    )
    celery_worker.conf.worker_hijack_root_logger = False
    return celery_worker


@inject
async def run_calculation_task(
    data: dict, worker_service: WorkerService = Provide[WorkerContainer.worker_service]
) -> None:
    await worker_service.run_calculation_async(data)


@inject
async def run_pipeline_task(
    data: dict, worker_service: WorkerService = Provide[WorkerContainer.worker_service]
) -> None:
    await worker_service.run_calculation_async(data)


init_worker_di()
worker = init_worker()


@worker.task
def calculation_task(data: dict) -> None:
    asyncio.run(run_calculation_task(data))


@worker.task
def pipeline_task(data: dict) -> None:
    asyncio.run(run_pipeline_task(data))
