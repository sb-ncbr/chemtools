import logging
import uuid

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException
from fastapi_utils.cbv import cbv

from api.schemas.calculation import TaskInfoResponseDto
from api.schemas.pipeline import CreatePipelineDto, PipelineDto, UpdatePipelineDto
from containers import AppContainer
from services.pipeline_service import PipelineService

logger = logging.getLogger(__name__)

pipelines_router = APIRouter(tags=["Pipelines"])


@cbv(pipelines_router)
class PipelinesRouter:
    @inject
    def __init__(self, pipeline_service: PipelineService = Depends(Provide[AppContainer.pipeline_service])):
        self.pipeline_service = pipeline_service

    @pipelines_router.get("/pipeline/{pipeline_id}")
    async def get_pipeline(self, pipeline_id: uuid.UUID) -> PipelineDto:
        if (pipeline := await self.pipeline_service.get_pipeline(pipeline_id)) is None:
            raise HTTPException(status_code=404, detail="Pipeline not found")
        return pipeline

    @pipelines_router.post("/pipeline", status_code=201)
    async def create_pipeline(self, data: CreatePipelineDto) -> PipelineDto:
        if (pipeline := await self.pipeline_service.create_pipeline(data)) is None:
            raise HTTPException(status_code=404, detail="User not found")
        return pipeline

    @pipelines_router.put("/pipeline/{pipeline_id}")
    async def update_pipeline(self, pipeline_id: uuid.UUID, data: UpdatePipelineDto) -> PipelineDto:
        if (pipeline := await self.pipeline_service.update_pipeline(pipeline_id, data)) is None:
            raise HTTPException(status_code=404, detail="Pipeline not found")
        return pipeline

    @pipelines_router.delete("/pipeline", status_code=204)
    async def delete_pipeline(self, pipeline_id: uuid.UUID) -> None:
        if not (await self.pipeline_service.delete_pipeline(pipeline_id)):
            raise HTTPException(status_code=404, detail="Pipeline not found")

    @pipelines_router.post("/pipeline/run")
    async def run_pipeline(self, pipeline_id: uuid.UUID) -> TaskInfoResponseDto:
        if (task_info := await self.pipeline_service.run_pipeline(pipeline_id)) is None:
            raise HTTPException(status_code=404, detail="Pipeline not found")
        return task_info
