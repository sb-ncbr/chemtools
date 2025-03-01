import logging
import uuid

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException
from fastapi_utils.cbv import cbv

from api.schemas.calculation import CalculationDto
from api.schemas.user import UserDto
from containers import AppContainer
from services.user_service import UserService

logger = logging.getLogger(__name__)

users_router = APIRouter(tags=["Users"])


@cbv(users_router)
class UsersRouter:
    @inject
    def __init__(self, user_service: UserService = Depends(Provide[AppContainer.user_service])):
        self.user_service = user_service

    @users_router.get("/users", response_model=list[UserDto])
    async def get_users(self) -> list[UserDto]:
        return await self.user_service.get_user_list()

    @users_router.get("/user", response_model=UserDto)
    async def get_user(self, user_id: uuid.UUID) -> UserDto:
        if (user := await self.user_service.get_user(user_id)) is None:
            raise HTTPException(status_code=404, detail="User not found")

        return UserDto.model_validate(user)

    @users_router.get("/user/calculations", response_model=list[CalculationDto])
    async def get_user_calculations(self, user_id: uuid.UUID) -> CalculationDto:
        if (user_calculations := await self.user_service.get_calculations(user_id)) is None:
            raise HTTPException(status_code=404, detail="User not found")

        return user_calculations
