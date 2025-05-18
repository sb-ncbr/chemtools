import logging
import uuid

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException
from fastapi_utils.cbv import cbv

from api.schemas.calculation import CalculationRequestDto
from di_containers import AppContainer
from services.calculation_service import CalculationService

logger = logging.getLogger(__name__)

calculations_router = APIRouter(tags=["Calculations"])


@cbv(calculations_router)
class CalculationsRouter:
    @inject
    def __init__(self, calculation_service: CalculationService = Depends(Provide["calculation_service"])):
        self.calculation_service = calculation_service

    @calculations_router.get("/calculation/{calculation_id}")
    async def get_calculation(self, calculation_id: uuid.UUID) -> CalculationRequestDto:
        try:
            return await self.calculation_service.get_calculation(calculation_id)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))

    @calculations_router.get("/user/{user_id}/calculations")
    async def get_user_calculations(self, user_id: uuid.UUID) -> list[CalculationRequestDto]:
        if (user_calculations := await self.calculation_service.get_user_calculations(user_id)) is None:
            raise HTTPException(status_code=404, detail="User not found")

        return user_calculations
