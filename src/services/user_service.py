import uuid

from api.schemas.calculation import CalculationRequestDto
from api.schemas.user import CreateUserDto, UserDto
from api.schemas.pipeline import PipelineDto
from db.models.user import UserModel
from db.repos.calculation_request_repo import CalculationRequestRepo
from db.repos.pipeline_repo import PipelineRepo
from db.repos.user_repo import UserRepo


class UserService:
    def __init__(
        self, user_repo: UserRepo, calculation_request_repo: CalculationRequestRepo, pipeline_repo: PipelineRepo
    ):
        self.user_repo = user_repo
        self.calculation_request_repo = calculation_request_repo
        self.pipeline_repo = pipeline_repo

    async def get_user_list(self) -> list[UserDto]:
        users = await self.user_repo.get_list()
        return [UserDto.model_validate(user) for user in users]

    async def get_user(self, user_id: uuid.UUID) -> UserDto | None:
        user = await self.user_repo.get_by_id(user_id)
        return UserDto.model_validate(user) if user else None

    async def create_user(self, user: CreateUserDto) -> UserDto:
        user = await self.user_repo.create(
            UserModel(**user.model_dump()),
        )
        return UserDto.model_validate(user)

    async def get_calculations(self, user_id: uuid.UUID) -> list[CalculationRequestDto] | None:
        if not await self.user_repo.get_by_id(user_id):
            return None

        user_calculations = await self.calculation_request_repo.filter_by(user_id=user_id)
        return [CalculationRequestDto.model_validate(calculation) for calculation in user_calculations]

    async def get_pipelines(self, user_id: uuid.UUID) -> list[PipelineDto] | None:
        if not await self.user_repo.get_by_id(user_id):
            return None

        user_pipelines = await self.pipeline_repo.get_pipelines_with_items(user_id=user_id)
        return [PipelineDto.model_validate(pipeline) for pipeline in user_pipelines]
