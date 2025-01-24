from dependency_injector.wiring import inject
from fastapi import APIRouter
from fastapi_utils.cbv import cbv

from api.enums import ChargeModeEnum
from api.schemas.charge import (
    ChargeBestParametersRequestDto,
    ChargeBestParametersResponseDto,
    ChargeInfoRequestDto,
    ChargeInfoResponseDto,
    ChargeRequestDto,
    ChargeResponseDto,
    ChargeSuitableMethodsRequestDto,
    ChargeSuitableMethodsResponseDto,
)
from api.schemas.gesamt import GesamtRequestDto, GesamtResponseDto
from api.schemas.mole import MoleRequestDto
from tools.chargefw2_tool import ChargeFW2Tool
from tools.gesamt_tool import GesamtTool
from tools.mole2_tool import Mole2Tool
from utils import from_app_container

tools_router = APIRouter(tags=["Tools"])


@cbv(tools_router)
class ToolsController:
    @inject
    def __init__(
        self,
        chargefw2_tool: ChargeFW2Tool = from_app_container("chargefw2_tool"),
        mole2_tool: Mole2Tool = from_app_container("mole2_tool"),
        gesamt_tool: GesamtTool = from_app_container("gesamt_tool"),
    ):
        self.__chargefw2_tool = chargefw2_tool
        self.__mole2_tool = mole2_tool
        self.__gesamt_tool = gesamt_tool

    @tools_router.get("/chargefw2/")
    async def chargefw2(self) -> dict[str, list[ChargeModeEnum]]:
        return {"available_modes": [mode for mode in ChargeModeEnum]}

    @tools_router.post("/chargefw2/info/")
    async def charge_info(
        self,
        data: ChargeInfoRequestDto,
    ) -> ChargeInfoResponseDto:
        chargefw2_output = await self.__chargefw2_tool.run(
            **data.model_dump(),
            mode=ChargeModeEnum.info,
        )
        parsed_data = self.__chargefw2_tool.parse_info_output(chargefw2_output)
        return ChargeInfoResponseDto(**parsed_data)

    @tools_router.post("/chargefw2/charges")
    async def charge_charges(
        self,
        data: ChargeRequestDto,
    ) -> ChargeResponseDto:

        chargefw2_output = await self.__chargefw2_tool.run(
            **data.model_dump(),
            mode=ChargeModeEnum.charges,
        )
        return ChargeResponseDto(**chargefw2_output)

    @tools_router.post("/chargefw2/suitable-methods")
    async def charge_suitable_methods(
        self,
        data: ChargeSuitableMethodsRequestDto,
    ) -> ChargeSuitableMethodsResponseDto:

        chargefw2_output = await self.__chargefw2_tool.run(
            **data.model_dump(),
            mode=ChargeModeEnum.suitable_methods,
        )
        methods, parameters = self.__chargefw2_tool.calculate_suitable_methods(chargefw2_output)
        return ChargeSuitableMethodsResponseDto(
            methods=methods,
            parameters=parameters,
        )

    @tools_router.post("/chargefw2/best-parameters")
    async def charge_best_parameters(
        self,
        data: ChargeBestParametersRequestDto,
    ) -> ChargeBestParametersResponseDto:
        chargefw2_output = await self.__chargefw2_tool.run(
            **data.model_dump(),
            mode=ChargeModeEnum.best_parameters,
        )
        return ChargeBestParametersResponseDto(result=chargefw2_output)

    @tools_router.post("/mole2/")
    async def mole_calculation(self, data: MoleRequestDto) -> dict:
        # await self.__mole2_tool.run(input_files=data.input_files, token=calculation_token, data=data)
        return {"status": "ok"}

    @tools_router.post("/gesamt/")
    async def gesamt_calculation(
        self,
        data: GesamtRequestDto,
    ) -> GesamtResponseDto:
        result = await self.__gesamt_tool.run(input_files=data.input_files)
        return result
