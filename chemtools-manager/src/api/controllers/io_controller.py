from typing import Annotated
import uuid
from fastapi import APIRouter, Depends, File
from fastapi_utils.cbv import cbv

from dependency_injector.wiring import Provide, inject
from api.models import UploadRequest, UploadResponse
from containers import ApplicationContainer
from services import FileStorageService

io_router = APIRouter(tags=["I/O"])


@cbv(io_router)
class IOController:
    @inject
    def __init__(
        self,
        storage_service: FileStorageService = Depends(Provide[ApplicationContainer.storage_service]),
    ):
        self.__storage_service = storage_service

    @io_router.post("/upload_files/")
    async def upload_files(self, data: Annotated[UploadRequest, File()]) -> UploadResponse:
        await self.__storage_service.upload_files(data)
        return UploadResponse(token=data.token)
