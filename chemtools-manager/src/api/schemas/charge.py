from pydantic import BaseModel

from api.schemas.base_tool import SingleFileRequestDto


class ChargeInfoRequestDto(SingleFileRequestDto):
    ignore_water: bool = False
    read_hetatm: bool = False


class ChargeRequestDto(SingleFileRequestDto):
    ignore_water: bool = False
    read_hetatm: bool = False
    permissive_types: bool = False
    method: str = ''
    parameter: str = ''


class ChargeBestParametersRequestDto(SingleFileRequestDto):
    ignore_water: bool = False
    read_hetatm: bool = False
    permissive_types: bool = False
    method: str


class ChargeSuitableMethodsRequestDto(SingleFileRequestDto):
    ignore_water: bool = False
    read_hetatm: bool = False
    permissive_types: bool = False


class ChargeInfoResponseDto(BaseModel):
    number_of_molecules: int
    number_of_atoms: int
    atom_counts: dict[str, int]


class ChargeResponseDto(BaseModel):
    mol2: str = None
    pqr: str = None
    txt: str = None
    cif: dict[str, str] = None


class ChargeBestParametersResponseDto(BaseModel):
    best_parameters: str | None


class ChargeSuitableMethodsResponseDto(BaseModel):
    methods: list[str]
    parameters: dict[str, list[str]]
