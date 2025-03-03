import logging
import uuid

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException
from fastapi_utils.cbv import cbv

from api.schemas.calculation import CalculationRequestDto
from api.schemas.pipeline import PipelineDto
from api.schemas.user import CreateUserDto, UserDto
from containers import AppContainer
from services.user_service import UserService

logger = logging.getLogger(__name__)

users_router = APIRouter(tags=["Users"])


@cbv(users_router)
class UsersRouter:
    @inject
    def __init__(self, user_service: UserService = Depends(Provide[AppContainer.user_service])):
        self.user_service = user_service

    @users_router.get("/users")
    async def get_users(self) -> list[UserDto]:
        return await self.user_service.get_user_list()

    @users_router.get("/user/{user_id}")
    async def get_user(self, user_id: uuid.UUID) -> UserDto:
        if (user := await self.user_service.get_user(user_id)) is None:
            raise HTTPException(status_code=404, detail="User not found")

        return UserDto.model_validate(user)

    @users_router.post("/user", status_code=201)
    async def create_user(self, data: CreateUserDto) -> UserDto:
        return await self.user_service.create_user(data)

    @users_router.get("/user/{user_id}/calculations")
    async def get_user_calculations(self, user_id: uuid.UUID) -> list[CalculationRequestDto]:
        if (user_calculations := await self.user_service.get_calculations(user_id)) is None:
            raise HTTPException(status_code=404, detail="User not found")

        return user_calculations

    @users_router.get("/user/{user_id}/pipelines")
    async def get_user_pipelines(self, user_id: uuid.UUID) -> list[PipelineDto]:
        if (user_pipelines := await self.user_service.get_pipelines(user_id)) is None:
            raise HTTPException(status_code=404, detail="User not found")

        return user_pipelines
