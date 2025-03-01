import uuid
from db.models.calculation import CalculationModel

from db.models.user import UserModel
from db.repos.user_repo import UserRepo


class UserService:
    def __init__(self, user_repo: UserRepo):
        self.user_repo = user_repo

    # TODO convert to UserDto
    async def get_user(self, user_id: uuid.UUID) -> UserModel:
        return await self.user_repo.get(user_id)

    async def get_calculations(self, user_id: uuid.UUID) -> list[CalculationModel]:
        return await self.user_repo.get_calculations(user_id)
