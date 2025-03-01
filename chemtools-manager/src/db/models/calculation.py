from datetime import datetime
from typing import TYPE_CHECKING, Optional
from enum import StrEnum
import uuid
from api.enums import DockerizedToolEnum
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.database import Base

if TYPE_CHECKING:
    from db.models import UserModel


class CalculationStatusEnum(StrEnum):
    pending = "pending"
    running = "running"
    success = "success"
    failure = "failure"


class CalculationModel(Base):
    __tablename__ = "calculations"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    tool_name: Mapped[DockerizedToolEnum]
    status: Mapped[CalculationStatusEnum] = mapped_column(default=CalculationStatusEnum.pending)
    result: Mapped[str | None]
    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    user_ip: Mapped[str | None]

    time_started: Mapped[datetime | None]
    time_finished: Mapped[datetime | None]

    user: Mapped[Optional["UserModel"]] = relationship(back_populates="calculations")
