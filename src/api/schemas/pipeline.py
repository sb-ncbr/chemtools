from datetime import datetime
from typing import Any
import uuid

from pydantic import BaseModel, ConfigDict

from api.enums import DockerizedToolEnum


class PipelineItemDto(BaseModel):
    id: uuid.UUID
    pipeline_id: uuid.UUID
    sequence_number: int
    tool_name: DockerizedToolEnum
    input_data: dict[str, Any]
    file_filter_regex: str | None = None

    model_config = ConfigDict(from_attributes=True)


class PipelineDto(BaseModel):
    id: uuid.UUID
    name: str
    user_id: uuid.UUID
    pipeline_items: list[PipelineItemDto]
    created_at: datetime
    modified_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CreatePipelineItemDto(BaseModel):
    pipeline_id: uuid.UUID
    sequence_number: int
    tool_name: DockerizedToolEnum
    input_data: dict[str, Any]
    file_filter_regex: str | None = None


class UpdatePipelineItemDto(BaseModel):
    sequence_number: int
    tool_name: DockerizedToolEnum
    input_data: dict[str, Any]
    file_filter_regex: str | None = None


class CreatePipelineDto(BaseModel):
    name: str
    user_id: uuid.UUID
    pipeline_items: list[CreatePipelineItemDto]


class UpdatePipelineDto(BaseModel):
    name: str
