import uuid

from api.schemas.calculation import TaskInfoResponseDto
from api.schemas.pipeline import CreatePipelineDto, PipelineDto, PipelineItemDto, UpdatePipelineDto
from db.models.pipeline import PipelineItemModel, PipelineModel
from db.repos.pipeline_repo import PipelineRepo
from db.repos.user_repo import UserRepo
from services.message_broker_service import MessageBrokerService


# TODO implement automatic model<->dto conversion
class PipelineService:
    def __init__(
        self,
        pipeline_repo: PipelineRepo,
        pipeline_item_repo: PipelineRepo,
        user_repo: UserRepo,
        message_broker_service: MessageBrokerService,
    ):
        self.pipeline_repo = pipeline_repo
        self.pipeline_item_repo = pipeline_item_repo
        self.user_repo = user_repo
        self.message_broker = message_broker_service

    async def get_pipeline(self, pipeline_id: uuid.UUID) -> PipelineDto | None:
        if (pipeline := await self.pipeline_repo.get_pipeline_with_items(pipeline_id)) is None:
            return None

        return PipelineDto(
            id=pipeline.id,
            user_id=pipeline.user_id,
            name=pipeline.name,
            pipeline_items=[
                PipelineItemDto(
                    id=item.id,
                    pipeline_id=item.pipeline_id,
                    sequence_number=item.sequence_number,
                    tool_name=item.tool_name,
                    input_data=item.input_data,
                    file_filter_regex=item.file_filter_regex,
                )
                for item in pipeline.pipeline_items
            ],
            created_at=pipeline.created_at,
            modified_at=pipeline.modified_at,
        )

    async def create_pipeline(self, create_pipeline_dto: CreatePipelineDto) -> PipelineDto | None:
        if (await self.user_repo.get_by_id(create_pipeline_dto.user_id)) is None:
            return None

        pipeline = await self.pipeline_repo.create(
            PipelineModel(
                name=create_pipeline_dto.name,
                user_id=create_pipeline_dto.user_id,
            )
        )
        # NOTE this could be optimized by using bulk insert
        pipeline_items = [
            await self.pipeline_item_repo.create(
                PipelineItemModel(
                    pipeline_id=pipeline.id,
                    sequence_number=item.sequence_number,
                    tool_name=item.tool_name,
                    input_data=item.input_data,
                    file_filter_regex=item.file_filter_regex,
                )
            )
            for item in create_pipeline_dto.pipeline_items
        ]
        return PipelineDto(
            id=pipeline.id,
            user_id=pipeline.user_id,
            name=pipeline.name,
            pipeline_items=[
                PipelineItemDto(
                    id=item.id,
                    pipeline_id=item.pipeline_id,
                    sequence_number=item.sequence_number,
                    tool_name=item.tool_name,
                    input_data=item.input_data,
                    file_filter_regex=item.file_filter_regex,
                )
                for item in pipeline_items
            ],
            created_at=pipeline.created_at,
            modified_at=pipeline.modified_at,
        )

    async def update_pipeline(
        self, pipeline_id: uuid.UUID, update_pipeline_dto: UpdatePipelineDto
    ) -> PipelineDto | None:
        if (pipeline := await self.pipeline_repo.get_pipeline_with_items(pipeline_id)) is None:
            return None

        await self.pipeline_repo.update(pipeline, name=update_pipeline_dto.name)

        return PipelineDto(
            id=pipeline_id,
            user_id=pipeline.user_id,
            name=pipeline.name,
            pipeline_items=[
                PipelineItemDto(
                    id=item.id,
                    pipeline_id=item.pipeline_id,
                    sequence_number=item.sequence_number,
                    tool_name=item.tool_name,
                    input_data=item.input_data,
                    file_filter_regex=item.file_filter_regex,
                )
                for item in pipeline.pipeline_items
            ],
            created_at=pipeline.created_at,
            modified_at=pipeline.modified_at,
        )

    async def delete_pipeline(self, pipeline_id: uuid.UUID) -> bool:
        if (pipeline := await self.pipeline_repo.get_by_id(pipeline_id)) is None:
            return False
        await self.pipeline_repo.delete(pipeline)
        return True

    async def run_pipeline(self, pipeline_id: uuid.UUID) -> TaskInfoResponseDto | None:
        if (pipeline := await self.pipeline_repo.get_pipeline_with_items(pipeline_id)) is None:
            return None

        self.message_broker.send_message(_task_name="worker.pipeline_task", data=pipeline.name, _priority=0)
        return {"info": "Pipeline task enqueued", "token": uuid.uuid4()}
