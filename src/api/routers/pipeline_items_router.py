import logging
import uuid

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException
from fastapi_utils.cbv import cbv

from api.schemas.pipeline import CreatePipelineItemDto, PipelineItemDto, UpdatePipelineItemDto
from containers import AppContainer
from services.pipeline_item_service import PipelineItemService

logger = logging.getLogger(__name__)

pipeline_items_router = APIRouter(tags=["Pipeline Items"])


@cbv(pipeline_items_router)
class PipelineItemsRouter:
    @inject
    def __init__(
        self, pipeline_item_service: PipelineItemService = Depends(Provide[AppContainer.pipeline_item_service])
    ):
        self.pipeline_item_service = pipeline_item_service

    @pipeline_items_router.post("/pipeline-item", status_code=201)
    async def create_pipeline_item(self, data: CreatePipelineItemDto) -> PipelineItemDto:
        if (pipeline_item := await self.pipeline_item_service.add_pipeline_item(data)) is None:
            raise HTTPException(status_code=404, detail="Pipeline not found")
        return pipeline_item

    @pipeline_items_router.put("/pipeline-item/{pipeline_item_id}", status_code=201)
    async def update_pipeline_item(self, pipeline_item_id: uuid.UUID, data: UpdatePipelineItemDto) -> PipelineItemDto:
        if (pipeline_item := await self.pipeline_item_service.update_pipeline_item(pipeline_item_id, data)) is None:
            raise HTTPException(status_code=404, detail="Pipeline item not found")
        return pipeline_item

    @pipeline_items_router.delete("/pipeline-item", status_code=204)
    async def delete_pipeline_item(self, pipeline_item_id: uuid.UUID) -> None:
        if not (await self.pipeline_item_service.delete_pipeline_item(pipeline_item_id)):
            raise HTTPException(status_code=404, detail="Pipeline item not found")
