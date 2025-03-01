import logging
import uuid

from api.schemas.calculation import CalculationDto
from containers import AppContainer
from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv
from dependency_injector.wiring import inject, Provide

from services.calculation_service import CalculationService

logger = logging.getLogger(__name__)

calculations_router = APIRouter(tags=["Calculations"])


@cbv(calculations_router)
class CalculationsRouter:
    @inject
    def __init__(self, calculation_service: CalculationService = Depends(Provide[AppContainer.calculation_service])):
        self.calculation_service = calculation_service

    @calculations_router.get("/calculation", response_model=CalculationDto)
    async def get_calculation(self, id: uuid.UUID) -> CalculationDto:
        return await self.calculation_service.get_calculation(id)
