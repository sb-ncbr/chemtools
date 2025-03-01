import uuid

from pydantic import BaseModel

from api.enums import DockerizedToolEnum
from db.models.calculation import CalculationStatusEnum


class CalculationDto(BaseModel):
    id: uuid.UUID
    tool_name: DockerizedToolEnum
    status: CalculationStatusEnum
    input_files: list[str] | None = None
    input_data: dict | None = None
    user_id: uuid.UUID | None = None
    result: str | None = None
