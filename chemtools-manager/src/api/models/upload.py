import uuid
from fastapi import UploadFile
from pydantic import BaseModel


class UploadRequest(BaseModel):
    files: list[UploadFile]


class UploadResponse(BaseModel):
    token: uuid.UUID
