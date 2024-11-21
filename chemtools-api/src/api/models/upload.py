import uuid
from fastapi import UploadFile
from pydantic import BaseModel


class UploadResponse(BaseModel):
    token: uuid.UUID


class UploadRequest(BaseModel):
    files: list[UploadFile]
    token: uuid.UUID
