import logging

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Request
from fastapi_utils.cbv import cbv

from api.enums import ChargeModeEnum, DockerizedToolEnum
from api.schemas.calculation import CreateCalculationRequestDto, TaskInfoResponseDto
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

logger = logging.getLogger(__name__)

tools_router = APIRouter(tags=["Tools"])


@cbv(tools_router)
class ToolsRouter:
    @inject
    def __init__(self, calculation_service: CalculationService = Depends(Provide[AppContainer.calculation_service])):
        self.calculation_service = calculation_service

    @tools_router.get("/chargefw2")
    async def chargefw2(self) -> dict[str, list[ChargeModeEnum]]:
        return {"available_modes": list(ChargeModeEnum)}

    @tools_router.post("/chargefw2/info")
    async def charge_info(
        self, request: Request, data: CreateCalculationRequestDto[ChargeInfoRequestDto]
    ) -> TaskInfoResponseDto:
        return await self.calculation_service.create_calculation(
            request, DockerizedToolEnum.chargefw2, data, mode=ChargeModeEnum.info
        )

    @tools_router.post("/chargefw2/charges")
    async def charge_charges(
        self, request: Request, data: CreateCalculationRequestDto[ChargeRequestDto]
    ) -> TaskInfoResponseDto:
        return await self.calculation_service.create_calculation(
            request, DockerizedToolEnum.chargefw2, data, mode=ChargeModeEnum.charges
        )

    @tools_router.post("/chargefw2/suitable-methods")
    async def charge_suitable_methods(
        self, request: Request, data: CreateCalculationRequestDto[ChargeSuitableMethodsRequestDto]
    ) -> TaskInfoResponseDto:
        return await self.calculation_service.create_calculation(
            request, DockerizedToolEnum.chargefw2, data, mode=ChargeModeEnum.suitable_methods
        )

    @tools_router.post("/chargefw2/best-parameters")
    async def charge_best_parameters(
        self, request: Request, data: CreateCalculationRequestDto[ChargeBestParametersRequestDto]
    ) -> TaskInfoResponseDto:
        return await self.calculation_service.create_calculation(
            request, DockerizedToolEnum.chargefw2, data, mode=ChargeModeEnum.best_parameters
        )

    @tools_router.post("/mole2")
    async def mole_calculation(
        self, request: Request, data: CreateCalculationRequestDto[MoleRequestDto]
    ) -> TaskInfoResponseDto:
        return await self.calculation_service.create_calculation(request, DockerizedToolEnum.mole2, data)

    @tools_router.post("/gesamt")
    async def gesamt_calculation(
        self, request: Request, data: CreateCalculationRequestDto[GesamtRequestDto]
    ) -> TaskInfoResponseDto:
        return await self.calculation_service.create_calculation(request, DockerizedToolEnum.gesamt, data)
