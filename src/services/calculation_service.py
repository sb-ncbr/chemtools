import json
import uuid

from fastapi import HTTPException, Request

from api.enums import RabbitQueueEnum
from api.schemas.calculation import CalculationRequestDto, CreateCalculationRequestDto, TaskInfoResponseDto
from conf.settings import AppSettings
from db.models.calculation import CalculationRequestModel, CalculationStatusEnum
from db.repos.calculation_request_repo import CalculationRequestRepo
from db.repos.calculation_result_repo import CalculationResultRepo
from services.file_cache_service import FileCacheService
from services.message_broker_service import MessageBrokerService
from services.pipeline_service import PipelineService
from utils import rename_dict_special


class CalculationService:
    def __init__(
        self,
        calculation_request_repo: CalculationRequestRepo,
        calculation_result_repo: CalculationResultRepo,
        message_broker_service: MessageBrokerService,
        file_cache_service: FileCacheService,
        pipeline_service: PipelineService,
        app_settings: AppSettings,
    ):
        self.calculation_request_repo = calculation_request_repo
        self.calculation_result_repo = calculation_result_repo
        self.message_broker = message_broker_service
        self.file_cache_service = file_cache_service
        self.pipeline_service = pipeline_service
        self.app_settings = app_settings

    async def create_calculation(
        self, request: Request, tool_name: str, data: CreateCalculationRequestDto, **additional_data
    ) -> TaskInfoResponseDto:
        client_host = request.client.host
        if data.pipeline_id:
            if client_host not in self.app_settings.PIPELINE_ACCEPTED_HOSTS.split(","):
                raise HTTPException(status_code=403, detail="Unauthorized to run pipeline calculations")
            if await self.pipeline_service.get_pipeline(data.pipeline_id) is None:
                raise HTTPException(status_code=404, detail=f"Pipeline with id {data.pipeline_id} not found")
            if not data.sequence_number:
                raise HTTPException(status_code=422, detail="Sequence number is required for pipeline calculations")

        input_data_dict = {**data.input_data.model_dump(), **additional_data}

        # Merge all input_files into a single list and remove them from the data dict.
        # If there is one input_file, it will be converted to a list of length 1.
        input_file = input_data_dict.pop("input_file", None)
        input_files = [*input_data_dict.pop("input_files", []), *([input_file] if input_file else [])]

        if not await self.file_cache_service.do_files_exist(input_files):
            raise HTTPException(status_code=404, detail="Input files do not exist")

        calculation = await self.calculation_request_repo.create(
            CalculationRequestModel(
                tool_name=tool_name,
                status=CalculationStatusEnum.pending,
                user_host=client_host,
                pipeline_id=data.pipeline_id,
                sequence_number=data.sequence_number,
                input_files=input_files,
                input_data=input_data_dict,
                user_id=data.user_id,
            )
        )
        calculation_dto = CalculationRequestDto.model_validate(calculation)

        if cached_result := await self.calculation_result_repo.get_cached_result(
            tool_name, input_files, input_data_dict
        ):
            await self.calculation_request_repo.update(
                calculation, calculation_result=cached_result, status=CalculationStatusEnum.cached
            )
            return TaskInfoResponseDto(info="Result cached from previous calculation", token=calculation_dto.id)

        await self.message_broker.send_calculation_message(
            data=json.loads(data),
            _queue=RabbitQueueEnum.pipeline_queue if calculation.pipeline_id else RabbitQueueEnum.free_queue,
        )
        return TaskInfoResponseDto(info="Calculation task enqueued", token=calculation_dto.id)

    async def get_calculation(self, calculation_id: uuid.UUID) -> CalculationRequestDto:
        if not (calculation := await self.calculation_request_repo.get_calculation_with_result(calculation_id)):
            raise ValueError("Calculation not found")

        return CalculationRequestDto.model_validate(calculation)

    async def get_user_calculations(self, user_id: uuid.UUID) -> list[CalculationRequestDto] | None:
        user_calculations = await self.calculation_request_repo.filter_by(user_id=user_id)
        return [CalculationRequestDto.model_validate(calculation) for calculation in user_calculations]
