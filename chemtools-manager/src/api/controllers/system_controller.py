from celery import Celery
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi_utils.cbv import cbv

from dependency_injector.wiring import Provide, inject

from containers import AppContainer

system_router = APIRouter(tags=["System"])


@cbv(system_router)
class SystemController:
    @system_router.get("/", response_class=HTMLResponse, include_in_schema=False)
    async def index(self, request: Request):
        return f"""
        <html>
            <h1>Chemtools Manager root</h1>
            <a href="{request.url}docs">Try API here</a>
        </html>
        """

    @system_router.get("/health")
    async def health(self):
        return {"status": "ok"}
