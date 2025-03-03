import uuid

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from db.models import CalculationRequestModel
from db.repos.base_repo import BaseRepo


class CalculationRequestRepo(BaseRepo):
    _model = CalculationRequestModel

    async def get_calculation_with_result(self, calculation_id: uuid.UUID) -> CalculationRequestModel:
        async with self.session_manager.session() as db:
            return (
                (
                    await db.execute(
                        select(self._model)
                        .where(CalculationRequestModel.id == calculation_id)
                        .options(selectinload(CalculationRequestModel.calculation_result))
                    )
                )
                .scalars()
                .first()
            )
