import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.enums import DockerizedToolEnum
from db.database import Base

if TYPE_CHECKING:
    from db.models import CalculationRequestModel, UserModel


class PipelineModel(Base):
    __tablename__ = "pipelines"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str]
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    modified_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

    user: Mapped["UserModel"] = relationship(back_populates="pipelines")
    pipeline_items: Mapped[list["PipelineItemModel"]] = relationship(back_populates="pipeline")
    calculation_requests: Mapped[list["CalculationRequestModel"]] = relationship(back_populates="pipeline")


class PipelineItemModel(Base):
    __tablename__ = "pipeline_items"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    sequence_number: Mapped[int]
    pipeline_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("pipelines.id"))
    tool_name: Mapped[DockerizedToolEnum]
    input_data: Mapped[dict[str, Any]] = mapped_column(JSON)

    file_filter_regex: Mapped[str | None]

    pipeline: Mapped["PipelineModel"] = relationship(back_populates="pipeline_items")
