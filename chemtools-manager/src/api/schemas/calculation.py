import uuid

from api.enums import DockerizedToolEnum
from pydantic import BaseModel, ConfigDict


class CalculationDto(BaseModel):
    id: uuid.UUID
    tool_name: DockerizedToolEnum
    user_id: uuid.UUID | None = None

    model_config = ConfigDict(from_attributes=True)
