import uuid
from sqlalchemy import select
from db.models import PipelineModel
from db.repos.base_repo import BaseRepo

from sqlalchemy.orm import selectinload


class PipelineRepo(BaseRepo):
    _model = PipelineModel

    # async def get_pipelines_with_items(self, pipeline_id: uuid.UUID) -> PipelineModel:
    #     async with self.session_manager.session() as db:
    #         result = await db.execute(
    #             select(PipelineModel)
    #             .where(PipelineModel.id == pipeline_id)
    #             .options(selectinload(PipelineModel.pipeline_items))
    #         )
    #         return result.scalar_one_or_none()

    async def get_pipelines_with_items(self, user_id: uuid.UUID) -> PipelineModel:
        async with self.session_manager.session() as db:
            return (
                (
                    await db.execute(
                        select(self._model)
                        .filter_by(user_id=user_id)
                        .options(selectinload(PipelineModel.pipeline_items))
                    )
                )
                .scalars()
                .all()
            )

    async def get_pipeline_with_items(self, pipeline_id: uuid.UUID) -> PipelineModel:
        async with self.session_manager.session() as db:
            return (
                (
                    await db.execute(
                        select(self._model)
                        .where(PipelineModel.id == pipeline_id)
                        .options(selectinload(PipelineModel.pipeline_items))
                    )
                )
                .scalars()
                .first()
            )
