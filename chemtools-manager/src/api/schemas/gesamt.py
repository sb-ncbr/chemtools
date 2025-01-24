from pydantic import BaseModel, Field

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
