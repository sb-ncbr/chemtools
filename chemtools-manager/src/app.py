import logging

import uvicorn
from fastapi import FastAPI

from conf.settings import AppSettings
import utils
from api.controllers import router_list
from containers import AppContainer
from dependency_injector.wiring import Provide, inject


def init_app_di() -> None:
    container = AppContainer()
    container.wire(
        modules=[
            __name__,
            "api.controllers.io_controller",
            "api.controllers.system_controller",
            "api.controllers.tools_controller",
            "containers",
        ]
    )


@inject
def init_logging(app_settings: AppSettings = Provide[AppContainer.app_settings]) -> None:
    logging.basicConfig(level=app_settings.LOG_LEVEL)
    config = utils.load_yml(utils.ROOT_DIR / "src/conf/logger.yml")
    logging.config.dictConfig(config)


@inject
def init_app(app_settings: AppSettings = Provide[AppContainer.app_settings]) -> FastAPI:
    app = FastAPI(title="ChemtoolsAPI", version=utils.get_project_version())
    for app_router in router_list:
        app.include_router(app_router)

    return app, app_settings


init_app_di()
init_logging()
app, app_settings = init_app()

if __name__ == "__main__":
    uvicorn.run(app, host=app_settings.APP_HOST, port=app_settings.APP_PORT)
