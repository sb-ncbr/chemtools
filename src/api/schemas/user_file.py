import uuid
from datetime import datetime

from fastapi import UploadFile
from pydantic import BaseModel, ConfigDict


class UserFileDto(BaseModel):
    id: uuid.UUID
    file_name: str
    file_name_hash: str
    user_id: uuid.UUID | None

    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UploadRequestDto(BaseModel):
    user_id: uuid.UUID | None = None
    files: list[UploadFile]


class UploadResponseDto(BaseModel):
    files: list[str]
