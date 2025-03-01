from pydantic import BaseModel, field_validator

from api.enums import MoleculeFileExtensionEnum, MoleculeRepoSiteEnum


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
