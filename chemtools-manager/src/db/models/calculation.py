from datetime import datetime
from typing import TYPE_CHECKING, Optional
from enum import StrEnum
import uuid
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.database import Base

if TYPE_CHECKING:
    from db.models.user import UserModel

class CalculationStatus(StrEnum):
    pending = "pending"
    running = "running"
    success = "success"
    failure = "failure"


class CalculationModel(Base):
    __tablename__ = "calculations"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    tool_name: Mapped[str]
    status: Mapped[CalculationStatus] = mapped_column(default=CalculationStatus.pending)
    result: Mapped[str | None]
    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))

    time_started: Mapped[datetime | None]
    time_finished: Mapped[datetime | None]

    user: Mapped[Optional["UserModel"]] = relationship(back_populates="calculations")
