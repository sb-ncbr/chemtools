import asyncio
from celery import Celery

from api.enums import DockerizedToolEnum
from conf.settings import RabbitMQSettings, WorkerSettings
import logging.config

from tools.chargefw2_tool import ChargeFW2Tool
from tools.gesamt_tool import GesamtTool
from tools.mole2_tool import Mole2Tool
import utils
from containers import WorkerContainer
from dependency_injector.wiring import Provide, inject


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
):
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


@app.task
def chemtool_task(_tool_name: DockerizedToolEnum, *args, **kwargs) -> None:
    dockerized_tool = get_dockerized_tool(_tool_name)
    print(f"Running tool: {dockerized_tool.image_name} with args: {args} and kwargs: {kwargs}")
    tool_result = asyncio.run(dockerized_tool.run(*args, **kwargs))
    print(tool_result)
    # TODO implement callback
    # requests.post(
    #     data.callback_url,
    #     json=tool_result.dict(),
    # )
