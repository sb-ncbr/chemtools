import uuid

from db.models.calculation import CalculationModel
from db.models.user import UserModel
from db.repos.base_repo import BaseRepo


class UserRepo(BaseRepo):
    _model = UserModel

    async def get_calculations(self, user_id: uuid.UUID) -> list[CalculationModel]:
        async with self.session_manager.session() as db:
            return db.query(CalculationModel).filter(CalculationModel.user_id == user_id).all()
