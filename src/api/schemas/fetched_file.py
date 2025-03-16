import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator

from api.enums import MoleculeFileExtensionEnum, MoleculeRepoSiteEnum


class FetchedFileDto(BaseModel):
    id: uuid.UUID
    molecule_id: str
    site: MoleculeRepoSiteEnum
    extension: MoleculeFileExtensionEnum
    file_name: str
    file_name_hash: str

    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FetchOnlineFileRequestDto(BaseModel):
    molecule_id: str
    site: MoleculeRepoSiteEnum
    extension: MoleculeFileExtensionEnum

    @field_validator("molecule_id")
    def check_molecule_id(cls, v):
        if not v or "?" in v:
            raise ValueError("invalid molecule_id")

        return v


class FetchOnlineFileResponseDto(BaseModel):
    file: str
    cached: bool
