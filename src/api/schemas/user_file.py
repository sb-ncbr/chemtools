import uuid
from datetime import datetime

from fastapi import UploadFile
from pydantic import BaseModel, ConfigDict, field_validator


class UserFileDto(BaseModel):
    id: uuid.UUID
    file_name: str
    file_name_hash: str
    user_id: uuid.UUID | None

    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DownloadRequestDto(BaseModel):
    user_id: uuid.UUID | None = None
    file_names: list[str]

    @field_validator("file_names")
    @classmethod
    def check_file_names(cls, v: list[str]) -> list[str]:
        if len(v) != len(set(v)):
            raise ValueError("Cannot download the same file multiple times")
        return v


class UploadRequestDto(BaseModel):
    user_id: uuid.UUID | None = None
    files: list[UploadFile]


class UploadResponseDto(BaseModel):
    files: list[str]
