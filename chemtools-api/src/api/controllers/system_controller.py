from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi_utils.cbv import cbv

system_router = APIRouter(tags=["System"])


@cbv(system_router)
class SystemController:
    @system_router.get("/", response_class=HTMLResponse)
    async def index(self, request: Request):
        return f'''
        <html>
            <h1>Chemtools API root</h1>
            <a href="{request.url}docs">Try API here</a>
        </html>
        '''

    @system_router.get("/health")
    async def health(self):
        return {"status": "ok"}
