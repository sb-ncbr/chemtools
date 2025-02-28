import logging

from utils import ROOT_DIR, get_project_version, load_yml
import uvicorn
from fastapi import FastAPI

from conf.settings import AppSettings
from api.routers import router_list
from containers import AppContainer
from dependency_injector.wiring import Provide, inject


def init_app_di() -> None:
    container = AppContainer()
    container.wire(
        modules=[
            __name__,
            "api.routers.io_router",
            "api.routers.system_router",
            "api.routers.tools_router",
            "containers",
        ]
    )


@inject
def init_logging(app_settings: AppSettings = Provide[AppContainer.app_settings]) -> None:
    logging.basicConfig(level=app_settings.LOG_LEVEL)
    config = load_yml(ROOT_DIR / "src/conf/logger.yml")
    logging.config.dictConfig(config)


@inject
def init_app(app_settings: AppSettings = Provide[AppContainer.app_settings]) -> FastAPI:
    app = FastAPI(title="ChemtoolsAPI", version=get_project_version())
    for app_router in router_list:
        app.include_router(app_router)

    return app, app_settings


init_app_di()
init_logging()
app, app_settings = init_app()

if __name__ == "__main__":
    uvicorn.run(app, host=app_settings.APP_HOST, port=app_settings.APP_PORT)
