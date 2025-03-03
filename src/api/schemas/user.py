import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserDto(BaseModel):
    id: uuid.UUID
    email: str
    first_name: str | None
    last_name: str | None
    full_name: str
    created_at: datetime
    modified_at: datetime

    is_active: bool
    is_superuser: bool

    queue_priority: int

    model_config = ConfigDict(from_attributes=True)


class CreateUserDto(BaseModel):
    email: str
    first_name: str | None
    last_name: str | None
    password_hash: str = ""
    is_active: bool = True
    is_superuser: bool = False
    queue_priority: int = 0
