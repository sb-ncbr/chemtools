import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from api.schemas.calculation import CalculationRequestDto


class PipelineDto(BaseModel):
    id: uuid.UUID
    name: str
    user_id: uuid.UUID
    calculation_requests: list[CalculationRequestDto]

    requested_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CreatePipelineDto(BaseModel):
    name: str
    user_id: uuid.UUID | None
