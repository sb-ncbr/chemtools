from fastapi import UploadFile
from pydantic import BaseModel, Field


class UploadRequestDto(BaseModel):
    files: list[UploadFile]


class UploadResponseDto(BaseModel):
    files: list[str]
