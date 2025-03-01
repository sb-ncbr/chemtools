import logging

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Request
from fastapi_utils.cbv import cbv

from api.enums import ChargeModeEnum, DockerizedToolEnum
from api.schemas.charge import (
    ChargeBestParametersRequestDto,
    ChargeInfoRequestDto,
    ChargeRequestDto,
    ChargeSuitableMethodsRequestDto,
)
from api.schemas.gesamt import GesamtRequestDto
from api.schemas.mole import MoleRequestDto
from containers import AppContainer
from services.calculation_service import CalculationService
from services.message_broker_service import MessageBrokerService

logger = logging.getLogger(__name__)

tools_router = APIRouter(tags=["Tools"])


@cbv(tools_router)
class ToolsRouter:
    @inject
    def __init__(
        self,
        calculation_service: CalculationService = Depends(Provide[AppContainer.calculation_service]),
        message_broker_service: MessageBrokerService = Depends(Provide[AppContainer.message_broker_service]),
    ):
        self.message_broker = message_broker_service
        self.calculation_service = calculation_service

    @tools_router.get("/chargefw2")
    async def chargefw2(self) -> dict[str, list[ChargeModeEnum]]:
        return {"available_modes": [mode for mode in ChargeModeEnum]}

    @tools_router.post("/chargefw2/info")
    async def charge_info(self, request: Request, data: ChargeInfoRequestDto) -> dict:
        calculation_dto = await self.calculation_service.create_calculation(
            request, {**data.model_dump(), "mode": ChargeModeEnum.info}, DockerizedToolEnum.chargefw2
        )
        self.message_broker.send_message(data=calculation_dto.model_dump(), _priority=0)
        return {"info": "task enqueued", "token": calculation_dto.id}

    @tools_router.post("/chargefw2/charges")
    async def charge_charges(self, request: Request, data: ChargeRequestDto) -> dict:
        calculation_dto = await self.calculation_service.create_calculation(
            request, {**data.model_dump(), "mode": ChargeModeEnum.charges}, DockerizedToolEnum.chargefw2
        )
        self.message_broker.send_message(data=calculation_dto.model_dump(), _priority=0)
        return {"info": "task enqueued", "token": calculation_dto.id}

    @tools_router.post("/chargefw2/suitable-methods")
    async def charge_suitable_methods(self, request: Request, data: ChargeSuitableMethodsRequestDto) -> dict:
        calculation_dto = await self.calculation_service.create_calculation(
            request, {**data.model_dump(), "mode": ChargeModeEnum.suitable_methods}, DockerizedToolEnum.chargefw2
        )
        self.message_broker.send_message(data=calculation_dto.model_dump(), _priority=0)
        return {"info": "task enqueued", "token": calculation_dto.id}

    @tools_router.post("/chargefw2/best-parameters")
    async def charge_best_parameters(self, request: Request, data: ChargeBestParametersRequestDto) -> dict:
        calculation_dto = await self.calculation_service.create_calculation(
            request, {**data.model_dump(), "mode": ChargeModeEnum.best_parameters}, DockerizedToolEnum.chargefw2
        )
        self.message_broker.send_message(data=calculation_dto.model_dump(), _priority=0)
        return {"info": "task enqueued", "token": calculation_dto.id}

    @tools_router.post("/mole2")
    async def mole_calculation(self, request: Request, data: MoleRequestDto) -> dict:
        await self.__mole2_tool.run(input_files=data.input_files, data=data)
        return {"info": "task enqueued"}

    @tools_router.post("/gesamt")
    async def gesamt_calculation(self, request: Request, data: GesamtRequestDto) -> dict:
        result = await self.__gesamt_tool.run(
            input_data=data.input_files, input_files=[file.file_name for file in data.input_files]
        )
        return {"info": "task enqueued"}
