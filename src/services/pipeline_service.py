import uuid

from fastapi import Request

from api.schemas.pipeline import CreatePipelineDto, PipelineDto
from db.models.pipeline import PipelineModel
from db.repos.pipeline_repo import PipelineRepo


class PipelineService:
    def __init__(self, pipeline_repo: PipelineRepo):
        self.pipeline_repo = pipeline_repo

    async def get_pipeline(self, pipeline_id: uuid.UUID) -> PipelineDto | None:
        pipeline = await self.pipeline_repo.get_pipeline_with_calculations(pipeline_id)
        return pipeline and PipelineDto.model_validate(pipeline)

    async def create_pipeline(self, request: Request, create_pipeline_dto: CreatePipelineDto) -> PipelineDto:
        pipeline = await self.pipeline_repo.create(
            PipelineModel(
                user_id=create_pipeline_dto.user_id,
                user_host=request.client.host,
            )
        )
        return PipelineDto.model_validate(pipeline)

    async def get_user_pipelines(self, user_id: uuid.UUID) -> list[PipelineDto]:
        user_pipelines = await self.pipeline_repo.get_pipelines_with_calculations(user_id=user_id)
        return [PipelineDto.model_validate(pipeline) for pipeline in user_pipelines]
