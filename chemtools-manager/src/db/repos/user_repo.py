import uuid
from db.models.user import UserModel
from db.repos.base_repo import BaseRepo
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.calculation import CalculationModel


class UserRepo(BaseRepo):
    def __init__(self, db: AsyncSession):
        super().__init__(db, UserModel)

    def get_calculations(self, user_id: uuid.UUID) -> list[CalculationModel]:
        return self.db.query(CalculationModel).filter(CalculationModel.user_id == user_id).all()
