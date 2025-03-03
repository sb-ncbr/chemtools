import uuid

from fastapi import Request

from api.enums import DockerizedToolEnum
from api.schemas.calculation import CalculationRequestDto, CalculationResultDto, TaskInfoResponseDto
from db.models.calculation import CalculationRequestModel, CalculationStatusEnum
from db.repos.calculation_request_repo import CalculationRequestRepo
from services.message_broker_service import MessageBrokerService


class CalculationService:
    def __init__(self, calculation_request_repo: CalculationRequestRepo, message_broker_service: MessageBrokerService):
        self.calculation_request_repo = calculation_request_repo
        self.message_broker = message_broker_service

    async def create_calculation(
        self, request: Request, data: dict, tool_name: DockerizedToolEnum
    ) -> TaskInfoResponseDto:
        # Merge all input_files into a single list and remove them from the data dict.
        # If there is one input_file, it will be converted to a list of length 1.
        input_file = data.pop("input_file", None)
        input_files = [*data.pop("input_files", []), *([input_file] if input_file else [])]

        calculation = await self.calculation_request_repo.create(
            CalculationRequestModel(
                tool_name=tool_name,
                status=CalculationStatusEnum.pending,
                user_host=request.client.host,
                input_files=input_files,
                input_data=data,
            ),
        )

        calculation_dto = CalculationRequestDto(
            id=calculation.id,
            input_files=input_files,
            input_data=data,
            tool_name=calculation.tool_name,
            user_id=calculation.user_id,
            status=calculation.status,
            requested_at=calculation.requested_at,
        )

        self.message_broker.send_message(
            _task_name="worker.calculation_task", data=calculation_dto.model_dump(), _priority=0
        )
        return {"info": "Calculation task enqueued", "token": calculation_dto.id}

    async def get_calculation(self, calculation_id: uuid.UUID) -> CalculationRequestDto:
        calculation = await self.calculation_request_repo.get_calculation_with_result(calculation_id)
        calculation_result = calculation.calculation_result
        return CalculationRequestDto(
            id=calculation.id,
            tool_name=calculation.tool_name,
            status=calculation.status,
            input_files=calculation.input_files,
            input_data=calculation.input_data,
            user_id=calculation.user_id,
            calculation_result=CalculationResultDto(
                id=calculation_result.id,
                output_files=calculation_result.output_files,
                output_data=calculation_result.output_data,
                started_at=calculation_result.started_at,
                finished_at=calculation_result.finished_at,
                # error_message=calculation_result.error_message,
            ),
            requested_at=calculation.requested_at,
        )
