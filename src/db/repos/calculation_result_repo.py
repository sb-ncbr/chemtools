from sqlalchemy import select
from sqlalchemy import cast
from sqlalchemy.dialects.postgresql import JSONB

from db.models.calculation import CalculationResultModel, CalculationRequestModel, CalculationStatusEnum
from db.repos.base_repo import BaseRepo


class CalculationResultRepo(BaseRepo):
    _model = CalculationResultModel

    async def get_cached_result(
        self, tool_name: str, input_files: list[str], data: dict
    ) -> CalculationResultModel | None:
        async with self.session_manager.session() as db:
            cached_result = (
                (
                    await db.execute(
                        select(CalculationRequestModel)
                        .join(self._model)
                        .filter(
                            CalculationRequestModel.status == CalculationStatusEnum.success,
                            CalculationRequestModel.tool_name == tool_name,
                            CalculationRequestModel.input_files == cast(input_files, JSONB),
                            CalculationRequestModel.input_data == cast(data, JSONB),
                        )
                    )
                )
                .scalars()
                .first()
            )
            return cached_result and cached_result.calculation_result
