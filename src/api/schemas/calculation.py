import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from api.enums import DockerizedToolEnum
from db.models.calculation import CalculationStatusEnum


class TaskInfoResponseDto(BaseModel):
    info: str
    token: uuid.UUID


class CalculationResultDto(BaseModel):
    id: uuid.UUID
    output_files: list[str]
    output_data: dict

    started_at: datetime
    finished_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CalculationRequestDto[ToolDataDtoT](BaseModel):
    id: uuid.UUID
    tool_name: DockerizedToolEnum
    status: CalculationStatusEnum

    input_files: list[str] | None = None
    input_data: ToolDataDtoT | None = None
    calculation_result: CalculationResultDto | None = None
    user_id: uuid.UUID | None = None
    pipeline_id: uuid.UUID | None = None
    sequence_number: int | None = None

    requested_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CreateCalculationRequestDto[ToolDataDtoT](BaseModel):
    pipeline_id: uuid.UUID | None = None
    sequence_number: int | None = None
    user_id: uuid.UUID | None = None
    input_data: ToolDataDtoT

    model_config = ConfigDict(from_attributes=True)
