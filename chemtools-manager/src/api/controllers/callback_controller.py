from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, File
from fastapi_utils.cbv import cbv

from api.schemas.calculation import CalculationRequestDto
from containers import AppContainer
from services import FileStorageService

callback_router = APIRouter(include_in_schema=False)


@cbv(callback_router)
class CallbackController:
    @inject
    def __init__(
        self,
        storage_service: FileStorageService = Depends(Provide[AppContainer.file_storage_service]),
    ):
        self.__storage_service = storage_service

    @callback_router.post("/complete_task/")
    async def complete_task(self, data: CalculationRequestDto) -> dict:
        return {"status": "success"}
