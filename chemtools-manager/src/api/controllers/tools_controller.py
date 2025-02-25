import logging

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
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
from services.message_broker_service import MessageBrokerService

logger = logging.getLogger(__name__)

tools_router = APIRouter(tags=["Tools"])


@cbv(tools_router)
class ToolsController:
    @inject
    def __init__(
        self,
        message_broker_service: MessageBrokerService = Depends(Provide[AppContainer.message_broker_service]),
    ):
        self.message_broker = message_broker_service

    @tools_router.get("/chargefw2/")
    async def chargefw2(self) -> dict[str, list[ChargeModeEnum]]:
        return {"available_modes": [mode for mode in ChargeModeEnum]}

    @tools_router.post("/chargefw2/info/")
    async def charge_info(self, data: ChargeInfoRequestDto) -> dict:
        self.message_broker.send_message(
            _tool_name=DockerizedToolEnum.chargefw2, **data.model_dump(), mode=ChargeModeEnum.info
        )
        return {"info": "task enqueued"}

    @tools_router.post("/chargefw2/charges")
    async def charge_charges(self, data: ChargeRequestDto) -> dict:
        self.message_broker.send_message(
            _tool_name=DockerizedToolEnum.chargefw2, **data.model_dump(), mode=ChargeModeEnum.charges
        )
        return {"info": "task enqueued"}

    @tools_router.post("/chargefw2/suitable-methods")
    async def charge_suitable_methods(self, data: ChargeSuitableMethodsRequestDto) -> dict:
        self.message_broker.send_message(
            _tool_name=DockerizedToolEnum.chargefw2, **data.model_dump(), mode=ChargeModeEnum.suitable_methods
        )
        return {"info": "task enqueued"}

    @tools_router.post("/chargefw2/best-parameters")
    async def charge_best_parameters(self, data: ChargeBestParametersRequestDto) -> dict:
        self.message_broker.send_message(
            _tool_name=DockerizedToolEnum.chargefw2, **data.model_dump(), mode=ChargeModeEnum.best_parameters
        )
        return {"info": "task enqueued"}

    @tools_router.post("/mole2/")
    async def mole_calculation(self, data: MoleRequestDto) -> dict:
        await self.__mole2_tool.run(input_files=data.input_files, data=data)
        return {"info": "task enqueued"}

    @tools_router.post("/gesamt/")
    async def gesamt_calculation(self, data: GesamtRequestDto) -> dict:
        result = await self.__gesamt_tool.run(
            input_data=data.input_files, input_files=[file.file_name for file in data.input_files]
        )
        return {"info": "task enqueued"}
