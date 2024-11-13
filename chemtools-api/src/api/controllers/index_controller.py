from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi_utils.cbv import cbv

index_router = APIRouter(tags=["Index"])


@cbv(index_router)
class IndexController:
    @index_router.get("/", response_class=HTMLResponse)
    async def index(self, request: Request):
        return f'''
        <html>
            <h1>Chemtools API root</h1>
            <a href="{request.url}docs">Try API here</a>
        </html>
        '''
