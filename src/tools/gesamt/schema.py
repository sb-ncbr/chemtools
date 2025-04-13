from pydantic import BaseModel, Field, model_validator

from api.schemas.base_tool import ManyFilesRequestDto


class GesamtResponseDto(BaseModel):
    q_score: float
    rmsd: float
    aligned_residues: int
    sequence_id: float
    rotation_matrix: list[list[float]]
    translation_vector: list[float]


class GesamtRequestDto(ManyFilesRequestDto):
    input_files: list[str] = Field(..., min_length=2)
    selection_strings: list[str | None] | None = None

    @model_validator(mode="before")
    def validate_input(cls, values: dict) -> dict:
        selection_strings = values.get("selection_strings") or []
        input_files = values.get("input_files") or []

        if not selection_strings:
            values["selection_strings"] = [None] * len(input_files)

        if len(input_files) != len(selection_strings):
            raise ValueError("input_files and selection_strings must have the same length")

        return values
