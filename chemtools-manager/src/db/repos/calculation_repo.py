from db.models.calculation import CalculationModel
from db.repos.base_repo import BaseRepo
from sqlalchemy.ext.asyncio import AsyncSession


class CalculationRepo(BaseRepo):
    def __init__(self, db: AsyncSession):
        super().__init__(db, CalculationModel)
