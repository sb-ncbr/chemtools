import uuid

from api.schemas.calculation import CalculationRequestDto
from api.schemas.pipeline import CreatePipelineDto, PipelineDto
from db.models.pipeline import PipelineModel
from db.repos.pipeline_repo import PipelineRepo


class PipelineService:
    def __init__(self, pipeline_repo: PipelineRepo):
        self.pipeline_repo = pipeline_repo

    async def get_pipeline(self, pipeline_id: uuid.UUID) -> PipelineDto | None:
        if (pipeline := await self.pipeline_repo.get_pipeline_with_calculations(pipeline_id)) is None:
            raise ValueError(f"Pipeline not found")

        return PipelineDto(
            id=pipeline.id,
            user_id=pipeline.user_id,
            name=pipeline.name,
            calculation_requests=[
                CalculationRequestDto.model_validate(calculation_request)
                for calculation_request in pipeline.calculation_requests
            ],
            requested_at=pipeline.requested_at,
        )

    async def create_pipeline(self, create_pipeline_dto: CreatePipelineDto) -> PipelineDto:
        pipeline = await self.pipeline_repo.create(
            PipelineModel(
                name=create_pipeline_dto.name,
                user_id=create_pipeline_dto.user_id,
            )
        )
        return PipelineDto(
            id=pipeline.id,
            name=pipeline.name,
            user_id=pipeline.user_id,
            requested_at=pipeline.requested_at,
            calculation_requests=[],
        )

    async def get_user_pipelines(self, user_id: uuid.UUID) -> list[PipelineDto]:
        user_pipelines = await self.pipeline_repo.get_pipelines_with_calculations(user_id=user_id)
        return [PipelineDto.model_validate(pipeline) for pipeline in user_pipelines]
