import uuid

from pydantic import BaseModel


class CalculationRequestDto(BaseModel):
    caculation_id: uuid.UUID
    result: str
