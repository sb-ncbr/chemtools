import uuid

from fastapi import UploadFile
from pydantic import BaseModel


class UploadRequestDto(BaseModel):
    files: list[UploadFile]


class UploadResponseDto(BaseModel):
    tokens: list[uuid.UUID]
