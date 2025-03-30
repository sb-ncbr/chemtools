import asyncio
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi_utils.cbv import cbv

from dependency_injector.wiring import inject, Provide

from containers import AppContainer
from services.healthcheck_service import HealthcheckService

system_router = APIRouter(tags=["System"])


@cbv(system_router)
class SystemRouter:
    @inject
    def __init__(self, health_check_service: HealthcheckService = Depends(Provide[AppContainer.health_check_service])):
        self.health_check_service = health_check_service

    @system_router.get("/", response_class=HTMLResponse, include_in_schema=False)
    async def index(self, request: Request):
        return f"""
        <html>
            <h1>Chemtools Manager root</h1>
            <a href="{request.url}docs">Try API here</a>
        </html>
        """

    @system_router.get("/health")
    async def health_check(self):
        responses = await asyncio.gather(
            self.health_check_service.postgres_health(),
            self.health_check_service.rabbitmq_health(),
            self.health_check_service.minio_health(),
        )
        if any(response["status"] != "UP" for response in responses):
            return JSONResponse(
                content={"status": "DOWN", "services": responses},
                status_code=503,
            )
        return JSONResponse(
            content={"status": "UP", "services": responses},
            status_code=200,
        )
