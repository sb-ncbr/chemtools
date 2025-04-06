from pydantic import BaseModel


class SingleFileRequestDto(BaseModel):
    input_file: str


class ManyFilesRequestDto(BaseModel):
    input_files: list[str]
