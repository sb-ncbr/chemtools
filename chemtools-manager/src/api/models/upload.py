import uuid
from fastapi import UploadFile
from pydantic import BaseModel


class UploadRequest(BaseModel):
    files: list[UploadFile]
    token: uuid.UUID


class UploadResponse(BaseModel):
    token: uuid.UUID
