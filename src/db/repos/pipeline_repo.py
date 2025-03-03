import uuid

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from db.models import PipelineModel
from db.repos.base_repo import BaseRepo


class PipelineRepo(BaseRepo):
    _model = PipelineModel

    async def get_pipelines_with_calculations(self, user_id: uuid.UUID) -> PipelineModel:
        async with self.session_manager.session() as db:
            return (
                (
                    await db.execute(
                        select(self._model)
                        .filter_by(user_id=user_id)
                        .options(selectinload(PipelineModel.calculation_requests))
                    )
                )
                .scalars()
                .all()
            )

    async def get_pipeline_with_calculations(self, pipeline_id: uuid.UUID) -> PipelineModel:
        async with self.session_manager.session() as db:
            return (
                (
                    await db.execute(
                        select(self._model)
                        .where(PipelineModel.id == pipeline_id)
                        .options(selectinload(PipelineModel.calculation_requests))
                    )
                )
                .scalars()
                .first()
            )
