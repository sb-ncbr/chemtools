import uuid
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class UserDto(BaseModel):
    id: uuid.UUID
    email: str
    first_name: str | None
    last_name: str | None
    full_name: str
    created_at: datetime
    updated_at: datetime

    is_active: bool
    is_superuser: bool

    queue_priority: int

    model_config = ConfigDict(from_attributes=True)
