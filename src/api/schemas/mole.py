from pydantic import BaseModel

from api.enums import MolePyMolChargePaletteEnum, MolePyMolSurfaceTypeEnum, MoleTunnelWeightFunctionEnum


class MoleCavityParams(BaseModel):
    ignore_het_atoms: bool = False
    ignore_hydrogens: bool = False
    interior_threshold: float = 1.25
    min_depth: int = 8
    min_depth_length: float = 5
    probe_radius: float = 3


class MoleTunnelParams(BaseModel):
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


class MoleExportOptions(BaseModel):
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


class MoleExitPoint(BaseModel):
    x: float
    y: float
    z: float


class MoleExit(BaseModel):
    points: list[MoleExitPoint]


class MoleDto(BaseModel):
    cavity: MoleCavityParams = MoleCavityParams()
    tunnel: MoleTunnelParams = MoleTunnelParams()
    export_options: MoleExportOptions = MoleExportOptions()
    custom_exits: list[MoleExit] | None = None
    custom_filter: str | None = None


class MoleRequestDto(MoleDto):
    input_file: str


# TODO support origins, paths and possibly other params
