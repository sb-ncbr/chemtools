from contextlib import asynccontextmanager

import uvicorn
from dependency_injector.wiring import Provide, inject
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import router_list
from conf.settings import AppSettings, PostgresSettings
from di_containers import AppContainer, TestContainer
from db.database import DatabaseSessionManager
from utils import get_project_version, init_app_di, init_logging


@inject
def init_app(
    container: AppContainer | TestContainer,
    app_settings: AppSettings = Provide["app_settings"],
    db_settings: PostgresSettings = Provide["postgres_settings"],
    session_manager: DatabaseSessionManager = Provide["session_manager"],
) -> FastAPI:
    @asynccontextmanager
    async def lifespan(_: FastAPI):
        yield
        if session_manager._engine is not None:
            await session_manager.close()

    init_logging(app_settings)
    session_manager.init(db_settings.postgres_url)
    app = FastAPI(title="ChemtoolsAPI", version=get_project_version(), lifespan=lifespan)
    app.container = container
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    for app_router in router_list:
        app.include_router(app_router)

    return app, app_settings


container = init_app_di()
app, app_settings = init_app(container=container)

if __name__ == "__main__":
    uvicorn.run(app, host=app_settings.APP_HOST, port=app_settings.APP_PORT)
