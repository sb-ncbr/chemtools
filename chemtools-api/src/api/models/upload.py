import uuid
from pydantic import BaseModel


class UploadRequest(BaseModel):
    token: uuid.UUID | None = None
