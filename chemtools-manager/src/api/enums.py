from enum import StrEnum


class ChargeModeEnum(StrEnum):
    info = "info"
    charges = "charges"
    best_parameters = "best-parameters"
    suitable_methods = "suitable-methods"


class MoleculeFileExtensionEnum(StrEnum):
    cif = "cif"
    pdb = "pdb"
    sdf = "sdf"


class MoleculeRepoSiteEnum(StrEnum):
    alphafold = "alphafold"
    rcsb_pdb = "rcsb_pdb"
    pubchem = "pubchem"

    def get_site_url(self) -> str:
        return {
            self.alphafold: "https://alphafold.ebi.ac.uk/files/{molecule_id}-model_v4.{extension}",
            self.rcsb_pdb: "https://files.rcsb.org/download/{molecule_id}.{extension}",
            self.pubchem: "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/CID/{molecule_id}/record/SDF?record_type=3d&response_type=save&response_basename=Conformer3D_COMPOUND_CID_{molecule_id}",
        }.get(self, "")

    def get_site_extensions(self) -> list[MoleculeFileExtensionEnum]:
        return {
            self.alphafold: [MoleculeFileExtensionEnum.pdb, MoleculeFileExtensionEnum.cif],
            self.rcsb_pdb: [MoleculeFileExtensionEnum.pdb, MoleculeFileExtensionEnum.cif],
            self.pubchem: [MoleculeFileExtensionEnum.sdf],
        }.get(self, [])


class MoleTunnelWeightFunctionEnum(StrEnum):
    voronoi_scale = "VoronoiScale"
    length_and_radius = "LengthAndRadius"
    length = "Length"
    constant = "Constant"


class MolePyMolSurfaceTypeEnum(StrEnum):
    surface = "Surface"
    spheres = "Spheres"


class MolePyMolChargePaletteEnum(StrEnum):
    red_white_blue = "RedWhiteBlue"
    blue_white_red = "BlueWhiteRed"
