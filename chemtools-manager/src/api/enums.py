import enum


class ChargeModeEnum(enum.StrEnum):
    charges = "charges"
    suitable_methods = "suitable-methods"


class MoleculeFileExtensionEnum(enum.StrEnum):
    cif = "cif"
    pdb = "pdb"
    sdf = "sdf"


class MoleculeRepoSiteEnum(enum.StrEnum):
    alphafold = "alphafold"
    rcsb = "rcsb"
    sm_prot = "sm-prot"
    pubchem = "pubchem"

    def get_site_url(self) -> str:
        return {
            self.alphafold: "https://alphafold.ebi.ac.uk/files/{molecule_id}-model_v4.{extension}",
            self.rcsb: "https://files.rcsb.org/download/{molecule_id}.{extension}",
            # TODO how to download from this site?
            # self.sm_prot: "http://bigdata.ibp.ac.cn/SmProt/search.php",
            self.pubchem: "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/CID/{molecule_id}/record/SDF?record_type=3d&response_type=save&response_basename=Conformer3D_COMPOUND_CID_{molecule_id}",
        }.get(self, "")

    def get_site_extensions(self) -> list[MoleculeFileExtensionEnum]:
        return {
            self.alphafold: [MoleculeFileExtensionEnum.pdb, MoleculeFileExtensionEnum.cif],
            self.rcsb: [MoleculeFileExtensionEnum.pdb, MoleculeFileExtensionEnum.cif],
            # TODO unknown extensions
            # self.sm_prot: [],
            self.pubchem: [MoleculeFileExtensionEnum.sdf],
        }.get(self, [])
