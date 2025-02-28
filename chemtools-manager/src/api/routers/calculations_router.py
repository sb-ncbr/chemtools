import logging
import uuid

from api.schemas.calculation import CalculationDto
from db.database import get_db
from db.repos.calculation_repo import CalculationRepo
from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

calculations_router = APIRouter(tags=["Calculations"])


@cbv(calculations_router)
class CalculationsRouter:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db
        self.calculation_repo = CalculationRepo(db)

    @calculations_router.get("/calculation", response_model=CalculationDto)
    async def get_calculation(self, id: uuid.UUID) -> CalculationDto:
        calculation = await self.calculation_repo.get_calculation(id)
        return CalculationDto.model_validate(calculation)
