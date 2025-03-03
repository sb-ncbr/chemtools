import uuid
from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

from api.enums import DockerizedToolEnum
from db.models.calculation import CalculationStatusEnum

ToolDataDto = TypeVar("ToolDataDto", bound=BaseModel)


class TaskInfoResponseDto(BaseModel):
    info: str
    token: uuid.UUID


class CalculationResultDto(BaseModel, Generic[ToolDataDto]):
    id: uuid.UUID
    output_files: list[str]

    output_data: ToolDataDto
    error_message: str | None = None

    started_at: datetime
    finished_at: datetime


class CalculationRequestDto(BaseModel, Generic[ToolDataDto]):
    id: uuid.UUID
    tool_name: DockerizedToolEnum
    status: CalculationStatusEnum

    input_files: list[str] | None = None
    input_data: ToolDataDto | None = None
    calculation_result: CalculationResultDto | None = None
    user_id: uuid.UUID | None = None
    pipeline_id: uuid.UUID | None = None
    sequence_number: int | None = None

    requested_at: datetime

    model_config = ConfigDict(from_attributes=True)
