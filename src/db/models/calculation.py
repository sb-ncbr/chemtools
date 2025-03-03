import uuid
from datetime import UTC, datetime
from enum import StrEnum
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import JSON, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.enums import DockerizedToolEnum
from db.database import Base

if TYPE_CHECKING:
    from db.models import UserModel
    from db.models import PipelineModel


class CalculationStatusEnum(StrEnum):
    pending = "pending"
    running = "running"
    success = "success"
    cached = "cached"
    failure = "failure"


class CalculationRequestModel(Base):
    __tablename__ = "calculation_requests"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tool_name: Mapped[DockerizedToolEnum]
    status: Mapped[CalculationStatusEnum] = mapped_column(default=CalculationStatusEnum.pending)
    input_files: Mapped[list[str]] = mapped_column(JSON)
    input_data: Mapped[dict[str, Any]] = mapped_column(JSON)

    result_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("calculation_results.id"))
    pipeline_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("pipelines.id"))
    file_filter_regex: Mapped[str | None]
    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    user_host: Mapped[str | None]

    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    calculation_result: Mapped[Optional["CalculationResultModel"]] = relationship(back_populates="calculation_requests")
    pipeline: Mapped[Optional["PipelineModel"]] = relationship(back_populates="calculation_requests")
    user: Mapped[Optional["UserModel"]] = relationship(back_populates="calculation_requests")


class CalculationResultModel(Base):
    __tablename__ = "calculation_results"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    output_files: Mapped[list[str]] = mapped_column(JSON)
    output_data: Mapped[dict[str, Any]] = mapped_column(JSON)

    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    calculation_requests: Mapped[list["CalculationRequestModel"]] = relationship(back_populates="calculation_result")
