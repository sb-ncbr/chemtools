from datetime import datetime
import asyncio
from api.schemas.calculation import CalculationDto
from celery import Celery

from api.enums import DockerizedToolEnum
from conf.const import ROOT_DIR
from conf.settings import PostgresSettings, RabbitMQSettings, WorkerSettings
import logging.config

from db.database import DatabaseSessionManager
from db.models.calculation import CalculationStatusEnum
from db.repos.calculation_repo import CalculationRepo
from tools.base_dockerized_tool import BaseDockerizedTool, ContainerRuntimeError
from tools.chargefw2_tool import ChargeFW2Tool
from tools.gesamt_tool import GesamtTool
from tools.mole2_tool import Mole2Tool

from utils import get_project_version, load_yml
from containers import WorkerContainer
from dependency_injector.wiring import Provide, inject

logger = logging.getLogger(__name__)


def init_worker_di() -> None:
    container = WorkerContainer()
    container.wire(
        modules=[
            __name__,
        ]
    )


@inject
def init_logging(worker_settings: WorkerSettings = Provide[WorkerContainer.worker_settings]):
    logging.basicConfig(level=worker_settings.LOG_LEVEL)
    config = load_yml(ROOT_DIR / "src/conf/logger.yml")
    logging.config.dictConfig(config)


@inject
def init_worker(rabbitmq_settings: RabbitMQSettings = Provide[WorkerContainer.rabbitmq_settings]) -> Celery:
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
def get_dockerized_tool(
    _tool_name: DockerizedToolEnum,
    chargefw2_tool: ChargeFW2Tool = Provide[WorkerContainer.chargefw2_tool],
    mole2_tool: Mole2Tool = Provide[WorkerContainer.mole2_tool],
    gesamt_tool: GesamtTool = Provide[WorkerContainer.gesamt_tool],
) -> BaseDockerizedTool:
    tool = {
        DockerizedToolEnum.chargefw2: chargefw2_tool,
        DockerizedToolEnum.mole2: mole2_tool,
        DockerizedToolEnum.gesamt: gesamt_tool,
    }.get(_tool_name)

    if not tool:
        raise NotImplementedError(f"Tool class not found for {_tool_name}")

    return tool


@inject
def get_session_manager(
    db_settings: PostgresSettings = Provide[WorkerContainer.postgres_settings],
    session_manager: DatabaseSessionManager = Provide[WorkerContainer.session_manager],
) -> DatabaseSessionManager:
    session_manager.init(db_settings.postgres_url)
    return session_manager


init_worker_di()
init_logging()
app = init_worker()


async def run_task_async(data: dict) -> None:
    calculation_dto = CalculationDto.model_validate(data)
    session_manager = get_session_manager()
    calculation_repo = CalculationRepo(session_manager)
    calculation = await calculation_repo.get_by_id(calculation_dto.id)
    await calculation_repo.update(
        calculation,
        tool_name=calculation_dto.tool_name,
        status=CalculationStatusEnum.running,
        time_started=datetime.now(),
    )

    dockerized_tool = get_dockerized_tool(calculation_dto.tool_name)
    logger.info(f"Running '{dockerized_tool.image_name}' tool by user={calculation_dto.user_id}")
    status = CalculationStatusEnum.success
    try:
        result = await dockerized_tool.run(
            token=calculation_dto.id,
            input_files=calculation_dto.input_files,
            user_id=calculation_dto.user_id,
            **calculation_dto.input_data,
        )

    except Exception as e:
        error_log = f"Tool '{dockerized_tool.image_name}' run by user={calculation_dto.user_id} failed with error: {e}"
        if isinstance(e, ContainerRuntimeError):
            logger.warning(error_log)
        else:
            logger.exception(error_log)
        result = str(e)
        status = CalculationStatusEnum.failure

    await calculation_repo.update(calculation, result=result, status=status, time_finished=datetime.now())


@app.task
def chemtool_task(data: dict) -> None:
    asyncio.run(run_task_async(data))
