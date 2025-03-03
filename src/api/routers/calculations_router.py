import logging
import uuid

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv

from api.schemas.calculation import CalculationRequestDto
from containers import AppContainer
from services.calculation_service import CalculationService

logger = logging.getLogger(__name__)

calculations_router = APIRouter(tags=["Calculations"])


@cbv(calculations_router)
class CalculationsRouter:
    @inject
    def __init__(self, calculation_service: CalculationService = Depends(Provide[AppContainer.calculation_service])):
        self.calculation_service = calculation_service

    @calculations_router.get("/calculation/{calculation_id}")
    async def get_calculation(self, calculation_id: uuid.UUID) -> CalculationRequestDto:
        return await self.calculation_service.get_calculation(calculation_id)
