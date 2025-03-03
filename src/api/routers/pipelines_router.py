import logging
import uuid

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException
from fastapi_utils.cbv import cbv

from api.schemas.calculation import TaskInfoResponseDto
from api.schemas.pipeline import CreatePipelineDto, PipelineDto
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
        try:
            return await self.pipeline_service.get_pipeline(pipeline_id)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))

    @pipelines_router.get("/user/{user_id}/pipelines")
    async def get_user_pipelines(self, user_id: uuid.UUID) -> list[PipelineDto]:
        return await self.pipeline_service.get_user_pipelines(user_id)

    @pipelines_router.post("/pipeline", status_code=201)
    async def create_pipeline(self, data: CreatePipelineDto) -> PipelineDto:
        return await self.pipeline_service.create_pipeline(data)
