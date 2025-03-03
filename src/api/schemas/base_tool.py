
from pydantic import BaseModel


class _BaseToolRequestDto(BaseModel):
    pass


class SingleFileRequestDto(BaseModel):
    input_file: str


class ManyFilesRequestDto(BaseModel):
    input_files: list[str]
