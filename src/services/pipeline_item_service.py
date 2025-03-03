import uuid

from api.schemas.pipeline import (
    CreatePipelineItemDto,
    PipelineItemDto,
    UpdatePipelineItemDto,
)
from db.models.pipeline import PipelineItemModel
from db.repos.pipeline_item_repo import PipelineItemRepo
from db.repos.pipeline_repo import PipelineRepo


class PipelineItemService:
    def __init__(self, pipeline_item_repo: PipelineItemRepo, pipeline_repo: PipelineRepo):
        self.pipeline_item_repo = pipeline_item_repo
        self.pipeline_repo = pipeline_repo

    async def add_pipeline_item(self, create_pipeline_item_dto: CreatePipelineItemDto) -> PipelineItemDto:
        if (await self.pipeline_repo.get_by_id(create_pipeline_item_dto.pipeline_id)) is None:
            return None

        pipeline_item = await self.pipeline_item_repo.create(
            PipelineItemModel(
                pipeline_id=create_pipeline_item_dto.pipeline_id,
                sequence_number=create_pipeline_item_dto.sequence_number,
                tool_name=create_pipeline_item_dto.tool_name,
                input_data=create_pipeline_item_dto.input_data,
                file_filter_regex=create_pipeline_item_dto.file_filter_regex,
            )
        )
        return PipelineItemDto(
            id=pipeline_item.id,
            pipeline_id=pipeline_item.pipeline_id,
            sequence_number=pipeline_item.sequence_number,
            tool_name=pipeline_item.tool_name,
            input_data=pipeline_item.input_data,
            file_filter_regex=pipeline_item.file_filter_regex,
        )

    async def update_pipeline_item(
        self, pipeline_item_id: uuid.UUID, update_pipeline_item_dto: UpdatePipelineItemDto
    ) -> PipelineItemDto:
        if (pipeline_item := await self.pipeline_item_repo.get_by_id(pipeline_item_id)) is None:
            return None

        await self.pipeline_item_repo.update(
            pipeline_item,
            sequence_number=update_pipeline_item_dto.sequence_number,
            tool_name=update_pipeline_item_dto.tool_name,
            input_data=update_pipeline_item_dto.input_data,
            file_filter_regex=update_pipeline_item_dto.file_filter_regex,
        )
        return PipelineItemDto(
            id=pipeline_item_id,
            pipeline_id=pipeline_item.pipeline_id,
            sequence_number=update_pipeline_item_dto.sequence_number,
            tool_name=update_pipeline_item_dto.tool_name,
            input_data=update_pipeline_item_dto.input_data,
            file_filter_regex=update_pipeline_item_dto.file_filter_regex,
        )

    async def delete_pipeline_item(self, pipeline_item_id: uuid.UUID) -> PipelineItemDto:
        if (pipeline_item := await self.pipeline_item_repo.get_by_id(pipeline_item_id)) is None:
            return False

        await self.pipeline_item_repo.delete(pipeline_item)
        return True
