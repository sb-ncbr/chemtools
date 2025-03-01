import uuid

from api.schemas.calculation import CalculationDto
from api.schemas.user import UserDto
from db.repos.user_repo import UserRepo


class UserService:
    def __init__(self, user_repo: UserRepo):
        self.user_repo = user_repo

    async def get_user_list(self) -> list[UserDto]:
        users = await self.user_repo.get_list()
        return [UserDto.model_validate(user) for user in users]

    async def get_user(self, user_id: uuid.UUID) -> UserDto | None:
        user = await self.user_repo.get_by_id(user_id)
        return UserDto.model_validate(user) if user else None

    async def get_calculations(self, user_id: uuid.UUID) -> list[CalculationDto] | None:
        if not await self.user_repo.get_by_id(user_id):
            return None

        user_calculations = await self.user_repo.get_calculations(user_id)
        return [CalculationDto.model_validate(calculation) for calculation in user_calculations]
