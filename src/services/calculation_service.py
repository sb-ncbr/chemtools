import uuid

from fastapi import Request

from api.enums import DockerizedToolEnum
from api.schemas.calculation import CalculationDto
from db.models.calculation import CalculationModel, CalculationStatusEnum
from db.repos.calculation_repo import CalculationRepo


class CalculationService:
    def __init__(self, calculation_repo: CalculationRepo):
        self.calculation_repo = calculation_repo

    async def create_calculation(self, request: Request, data: dict, tool_name: DockerizedToolEnum) -> CalculationDto:
        calculation = await self.calculation_repo.create(
            CalculationModel(
                tool_name=tool_name,
                status=CalculationStatusEnum.pending,
                user_ip=request.client.host,
            ),
        )
        # Merge all input_files into a single list and remove them from the data dict.
        # If there is one input_file, it will be converted to a list of length 1.
        input_file = data.pop("input_file", None)
        input_files = [*data.pop("input_files", []), *([input_file] if input_file else [])]

        return CalculationDto(
            id=calculation.id,
            input_files=input_files,
            input_data=data,
            tool_name=calculation.tool_name,
            user_id=calculation.user_id,
            status=calculation.status,
        )

    async def get_calculation(self, calculation_id: uuid.UUID) -> CalculationDto:
        calculation = await self.calculation_repo.get_by_id(calculation_id)
        return CalculationDto(
            id=calculation.id,
            tool_name=calculation.tool_name,
            user_id=calculation.user_id,
            status=calculation.status,
            result=calculation.result,
        )
