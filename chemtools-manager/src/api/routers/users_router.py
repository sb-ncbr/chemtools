from api.schemas.user import UserDto
from fastapi import HTTPException
import logging
import uuid

from api.schemas.calculation import CalculationDto
from db.repos.user_repo import UserRepo
from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv

from dependency_injector.wiring import Provide, inject
from services.user_service import UserService

logger = logging.getLogger(__name__)

users_router = APIRouter(tags=["Users"])


@cbv(users_router)
class UsersRouter:
    @inject
    def __init__(self, user_service: UserService = Depends(Provide[UserService])):
        self.user_service = user_service

    @users_router.get("/users", response_model=list[UserDto])
    async def get_users(self) -> list[UserDto]:
        users = await self.user_service.get_user_list()
        return [UserDto.model_validate(user) for user in users]

    @users_router.get("/user", response_model=UserDto)
    async def get_user(self, id: uuid.UUID) -> UserDto:
        user = await self.user_service.get_user(id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        return UserDto.model_validate(user)

    @users_router.get("/user/calculations", response_model=list[CalculationDto])
    async def get_user_calculations(self, id: uuid.UUID) -> CalculationDto:
        user_calculations = await self.user_service.get_calculations(id)
        return [CalculationDto.model_validate(calculation) for calculation in user_calculations]
