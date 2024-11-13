import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

from api.controllers import router_list
from containers import ApplicationContainer
import settings
import utils


def init_db(app) -> None:
    register_tortoise(
        app,
        db_url=settings.POSTGRES_DB_URL,
        modules={"models": ["db.models"]},
        generate_schemas=False,
        add_exception_handlers=True,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.config.dictConfig(utils.load_yml("conf/logging.yml"))

    init_db(app)

    container = ApplicationContainer()
    container.wire(modules=["api.controllers.charge_controller", "api.controllers.io_controller"])

    yield


def create_app():
    app = FastAPI(redoc_url=None, lifespan=lifespan)
    for app_router in router_list:
        app.include_router(app_router)

    return app


app = create_app()
