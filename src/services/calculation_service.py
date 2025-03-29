import json
import uuid

from fastapi import HTTPException, Request

from api.enums import DockerizedToolEnum
from api.schemas.calculation import CalculationRequestDto, TaskInfoResponseDto
from db.models.calculation import CalculationRequestModel, CalculationStatusEnum
from db.repos.calculation_request_repo import CalculationRequestRepo
from db.repos.calculation_result_repo import CalculationResultRepo
from services.file_cache_service import FileCacheService
from services.message_broker_service import MessageBrokerService


class CalculationService:
    def __init__(
        self,
        calculation_request_repo: CalculationRequestRepo,
        calculation_result_repo: CalculationResultRepo,
        message_broker_service: MessageBrokerService,
        file_cache_service: FileCacheService,
    ):
        self.calculation_request_repo = calculation_request_repo
        self.calculation_result_repo = calculation_result_repo
        self.message_broker = message_broker_service
        self.file_cache_service = file_cache_service

    async def create_calculation(
        self, request: Request, data: dict, tool_name: DockerizedToolEnum
    ) -> TaskInfoResponseDto:
        # Merge all input_files into a single list and remove them from the data dict.
        # If there is one input_file, it will be converted to a list of length 1.
        input_files = [data.pop("input_file", None)] or [*data.pop("input_files", [])]

        if not await self.file_cache_service.do_files_exist(input_files):
            raise HTTPException(status_code=404, detail="Input files do not exist")

        calculation = await self.calculation_request_repo.create(
            CalculationRequestModel(
                tool_name=tool_name,
                status=CalculationStatusEnum.pending,
                user_host=request.client.host,
                input_files=input_files,
                input_data=data,
            )
        )
        calculation_dto = CalculationRequestDto.model_validate(calculation)

        if cached_result := await self.calculation_result_repo.get_cached_result(tool_name, input_files, data):
            await self.calculation_request_repo.update(
                calculation, calculation_result=cached_result, status=CalculationStatusEnum.cached
            )
            return TaskInfoResponseDto(info="Result cached from previous calculation", token=calculation_dto.id)

        await self.message_broker.send_calculation_message(
            data=json.loads(calculation_dto.model_dump_json()),
            _queue="pipeline_queue" if calculation.pipeline_id else "free_queue",
        )
        return TaskInfoResponseDto(info="Calculation task enqueued", token=calculation_dto.id)

    async def get_calculation(self, calculation_id: uuid.UUID) -> CalculationRequestDto:
        if not (calculation := await self.calculation_request_repo.get_calculation_with_result(calculation_id)):
            raise ValueError("Calculation not found")

        return CalculationRequestDto.model_validate(calculation)

    async def get_user_calculations(self, user_id: uuid.UUID) -> list[CalculationRequestDto] | None:
        user_calculations = await self.calculation_request_repo.filter_by(user_id=user_id)
        return [CalculationRequestDto.model_validate(calculation) for calculation in user_calculations]
