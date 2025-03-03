from datetime import datetime
from typing import Any
import uuid

from pydantic import BaseModel

from api.enums import DockerizedToolEnum
from db.models.calculation import CalculationStatusEnum


class TaskInfoResponseDto(BaseModel):
    info: str
    token: uuid.UUID


class CalculationResultDto(BaseModel):
    id: uuid.UUID
    output_files: list[str]
    output_data: str | None = None
    started_at: datetime
    finished_at: datetime
    error_message: str | None = None


class CalculationRequestDto(BaseModel):
    id: uuid.UUID
    tool_name: DockerizedToolEnum
    status: CalculationStatusEnum
    input_files: list[str] | None = None
    input_data: dict | None = None
    user_id: uuid.UUID | None = None
    calculation_result: CalculationResultDto | None = None
    # pipeline_id: uuid.UUID | None = None
    # pipeline_item_id: uuid.UUID | None = None
    requested_at: datetime
