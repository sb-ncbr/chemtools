from contextlib import asynccontextmanager

from db.database import DatabaseSessionManager
from utils import get_project_version, init_app_di, init_logging
import uvicorn
from fastapi import FastAPI

from conf.settings import AppSettings, PostgresSettings
from api.routers import router_list
from containers import AppContainer
from dependency_injector.wiring import Provide, inject


@inject
def init_app(
    app_settings: AppSettings = Provide[AppContainer.app_settings],
    db_settings: PostgresSettings = Provide[AppContainer.postgres_settings],
    session_manager: DatabaseSessionManager = Provide[AppContainer.session_manager],
) -> FastAPI:
    @asynccontextmanager
    async def lifespan(_: FastAPI):
        yield
        if session_manager._engine is not None:
            await session_manager.close()

    init_logging(app_settings)
    session_manager.init(db_settings.postgres_url)
    app = FastAPI(title="ChemtoolsAPI", version=get_project_version(), lifespan=lifespan)
    for app_router in router_list:
        app.include_router(app_router)

    return app, app_settings


init_app_di()
app, app_settings = init_app()

if __name__ == "__main__":
    uvicorn.run(app, host=app_settings.APP_HOST, port=app_settings.APP_PORT)
