import uuid

from pydantic import BaseModel
from pydantic_xml import BaseXmlModel, RootXmlModel

from api.enums import MolePyMolChargePaletteEnum, MolePyMolSurfaceTypeEnum, MoleTunnelWeightFunctionEnum


# TODO get rid of this temporary hack.
# Probably use pydantic-xml package
class DataToStrMixin:
    def __getattribute__(self, name):
        value = super().__getattribute__(name)
        if isinstance(value, bool):
            return str(int(value))
        elif isinstance(value, (float, int)):
            return str(value)
        return value


class MoleCavityParams(BaseXmlModel):
    ignore_het_atoms: bool = False
    ignore_hydrogens: bool = False
    interior_threshold: float = 1.25
    min_depth: int = 8
    min_depth_length: float = 5
    probe_radius: float = 3


class MoleTunnelParams(BaseXmlModel):
    auto_origin_cover_radius: float = 10
    bottleneck_radius: float = 1.25
    bottleneck_tolerance: float = 0
    filter_boundary_layers: bool = False
    max_auto_origins_per_cavity: int = 5
    max_tunnel_similarity: float = 0.9
    min_pore_length: float = 0
    min_tunnel_length: float = 0
    origin_radius: float = 5
    surface_cover_radius: float = 10
    use_custom_exits_only: bool = False
    weight_function: MoleTunnelWeightFunctionEnum = MoleTunnelWeightFunctionEnum.voronoi_scale


class MoleExportOptions(BaseXmlModel):
    # Formats
    charge_surface: bool = True
    chimera: bool = False
    create_csv: bool = False
    create_json: bool = False
    mesh: bool = False
    pdb_profile: bool = False
    pdb_structure: bool = False
    pymol: bool = False
    vmd: bool = False

    # Mesh
    compress: bool = False
    density: float = 1.33

    # PyMol
    charge_palette: MolePyMolChargePaletteEnum = MolePyMolChargePaletteEnum.red_white_blue
    surface_type: MolePyMolSurfaceTypeEnum = MolePyMolSurfaceTypeEnum.surface

    # Types
    cavities: bool = True
    pores_auto: bool = False
    pores_merged: bool = False
    pores_user: bool = False
    tunnels: bool = True


class MoleExitPoint(BaseXmlModel):
    X: float
    Y: float
    Z: float


class MoleExit(BaseXmlModel):
    points: list[MoleExitPoint]


class MoleRequestDto(BaseXmlModel):
    cavity: MoleCavityParams = MoleCavityParams()
    tunnel: MoleTunnelParams = MoleTunnelParams()
    export_options: MoleExportOptions = MoleExportOptions()
    custom_exits: list[MoleExit] | None = None
    custom_filter: str | None = None

    # TODO maybe support origins and paths


class TunnelsDto(RootXmlModel):
    input


class MoleResponseDto(BaseModel):
    token: uuid.UUID
