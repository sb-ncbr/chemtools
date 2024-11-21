from typing import Annotated
from fastapi import APIRouter, File, Form, Request, Depends, UploadFile
from fastapi_utils.cbv import cbv

from dependency_injector.wiring import Provide, inject
from api.models import UploadResponse
from api.models.upload import UploadRequest
from clients.chemtools_manager_client import ChemtoolsManagerClient
from containers import ApplicationContainer

io_router = APIRouter(tags=["I/O"])


@cbv(io_router)
class IOController:
    @inject
    def __init__(
        self,
        chemtools_manager_client: ChemtoolsManagerClient = Depends(
            Provide[ApplicationContainer.chemtools_manager_client]
        ),
    ):
        self.__chemtools_manager_client = chemtools_manager_client

    @io_router.post("/upload_files")
    async def upload_files(self, data: Annotated[UploadRequest, File()]) -> UploadResponse:
        response = await self.__chemtools_manager_client.upload_files(data)
        return response
