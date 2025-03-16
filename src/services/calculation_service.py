import uuid

from fastapi import HTTPException, Request

from api.enums import DockerizedToolEnum
from api.schemas.calculation import CalculationRequestDto, CalculationResultDto, TaskInfoResponseDto
from db.models.calculation import CalculationRequestModel, CalculationStatusEnum
from db.repos.calculation_request_repo import CalculationRequestRepo
from services.file_cache_service import FileCacheService
from services.message_broker_service import MessageBrokerService


class CalculationService:
    def __init__(
        self,
        calculation_request_repo: CalculationRequestRepo,
        message_broker_service: MessageBrokerService,
        file_cache_service: FileCacheService,
    ):
        self.calculation_request_repo = calculation_request_repo
        self.message_broker = message_broker_service
        self.file_cache_service = file_cache_service

    async def create_calculation(
        self, request: Request, data: dict, tool_name: DockerizedToolEnum
    ) -> TaskInfoResponseDto:
        # Merge all input_files into a single list and remove them from the data dict.
        # If there is one input_file, it will be converted to a list of length 1.
        input_file = data.pop("input_file", None)
        input_files = [*data.pop("input_files", []), *([input_file] if input_file else [])]

        if not await self.file_cache_service.do_files_exist(input_files):
            raise HTTPException(status_code=404, detail="Input files do not exist")

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

        self.message_broker.send_calculation_message(
            data=calculation_dto.model_dump(),
            _queue="pipeline_queue" if calculation.pipeline_id else "free_queue",
        )
        return TaskInfoResponseDto(info="Calculation task enqueued", token=calculation_dto.id)

    async def get_calculation(self, calculation_id: uuid.UUID) -> CalculationRequestDto:
        if not (calculation := await self.calculation_request_repo.get_calculation_with_result(calculation_id)):
            raise ValueError("Calculation not found")

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

    async def get_user_calculations(self, user_id: uuid.UUID) -> list[CalculationRequestDto] | None:
        user_calculations = await self.calculation_request_repo.filter_by(user_id=user_id)
        return [CalculationRequestDto.model_validate(calculation) for calculation in user_calculations]
