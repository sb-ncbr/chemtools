import uuid

from pydantic import BaseModel


class _BaseToolRequestDto(BaseModel):
    calculation_id: uuid.UUID
    order: int


class SingleFileRequestDto(_BaseToolRequestDto):
    input_file: str


class ManyFilesRequestDto(_BaseToolRequestDto):
    input_files: list[str]
