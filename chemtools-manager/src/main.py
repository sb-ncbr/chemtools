import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

import utils
from api.controllers import router_list
from containers import ApplicationContainer


@asynccontextmanager
async def lifespan(_: FastAPI):
    logging.config.dictConfig(utils.load_yml("conf/logger.yml"))

    container = ApplicationContainer()
    container.wire(
        modules=[
            "api.controllers.io_controller",
            "api.controllers.tools_controller",
        ]
    )
    yield


def init_logging() -> None:
    # TODO add this to env with default INFO
    logging.basicConfig(level=logging.DEBUG)
    config = utils.load_yml("conf/logger.yml")
    logging.config.dictConfig(config)


def init_app() -> FastAPI:
    app = FastAPI(redoc_url=None, lifespan=lifespan)
    for app_router in router_list:
        app.include_router(app_router)

    return app


init_logging()
app = init_app()
