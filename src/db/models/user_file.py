import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column

from db.database import Base


class UserFileModel(Base):
    __tablename__ = "user_files"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    file_name: Mapped[str]
    file_name_hash: Mapped[str]
    user_id: Mapped[uuid.UUID | None]

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    def __repr__(self) -> str:
        return f"UserFileModel(id={self.id}, file_name={self.file_name} file_name_hash={self.file_name_hash})"
