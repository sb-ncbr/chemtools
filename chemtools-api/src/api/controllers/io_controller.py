import uuid
from fastapi import APIRouter, Request
from fastapi_utils.cbv import cbv

from api.models import UploadRequest

io_router = APIRouter(tags=["I/O"])


@cbv(io_router)
class IOController:
    @io_router.post("/upload_files")
    async def upload_files(
        data: UploadRequest,
        # file: Annotated[UploadFile, File] | None = None,
    ):
        token = data.token or str(uuid.uuid4())
        return
