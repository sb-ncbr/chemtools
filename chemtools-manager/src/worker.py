from datetime import datetime
import asyncio
from api.schemas.calculation import CalculationDto
from celery import Celery

from api.enums import DockerizedToolEnum
from conf.settings import RabbitMQSettings, WorkerSettings
import logging.config

from db.models.calculation import CalculationStatus
from db.repos.calculation_repo import CalculationRepo
from tools.base_dockerized_tool import BaseDockerizedTool
from tools.chargefw2_tool import ChargeFW2Tool
from tools.gesamt_tool import GesamtTool
from tools.mole2_tool import Mole2Tool
import utils
from containers import WorkerContainer
from dependency_injector.wiring import Provide, inject

from db.database import sessionmanager

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
    config = utils.load_yml(utils.ROOT_DIR / "src/conf/logger.yml")
    logging.config.dictConfig(config)


@inject
def init_worker(rabbitmq_settings: RabbitMQSettings = Provide[WorkerContainer.rabbitmq_settings]) -> Celery:
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


init_worker_di()
init_logging()
app = init_worker()


async def run_task_async(calculation_dto: CalculationDto) -> None:
    with sessionmanager.session() as db:
        calculation_repo = CalculationRepo(db)
        calculation = await calculation_repo.get_or_create(
            calculation_dto.id,
            **calculation_dto.model_dump(),
            status=CalculationStatus.running,
            time_started=datetime.now()
        )

        dockerized_tool = get_dockerized_tool(calculation_dto.tool_name)
        logger.info(f"Running '{dockerized_tool.image_name}' tool by user={calculation_dto.user_id}")
        status = CalculationStatus.success
        try:
            result = await dockerized_tool.run(calculation_dto.id, **calculation_dto.model_dump())
        except Exception as e:
            logger.error(f"Tool '{dockerized_tool.image_name}' failed with error: {e}")
            result = str(e)
            status = CalculationStatus.failure

        calculation_repo.update(calculation, result=result, status=status, time_finished=datetime.now())


@app.task
def chemtool_task(*args, **kwargs) -> None:
    asyncio.run(run_task_async(*args, **kwargs))
