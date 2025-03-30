import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column

from api.enums import MoleculeFileExtensionEnum, MoleculeRepoSiteEnum
from db.database import Base


class FetchedFileModel(Base):
    __tablename__ = "fetched_files"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    file_name: Mapped[str]
    file_name_hash: Mapped[str]

    molecule_id: Mapped[str]
    site: Mapped[MoleculeRepoSiteEnum]
    extension: Mapped[MoleculeFileExtensionEnum]

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    def __repr__(self) -> str:
        return f"FetchedFileModel(id={self.id}, file_name={self.file_name} hash={self.file_name_hash} site={self.site}"
