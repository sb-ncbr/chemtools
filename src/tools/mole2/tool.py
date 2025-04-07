import os
import shutil
import uuid

from lxml import etree
from lxml.builder import E

from conf.const import ROOT_DIR
from tools.dockerized_tool_base import DockerizedToolBase
from tools.mole2.schema import MoleDto
from utils import to_str


class Mole2Tool(DockerizedToolBase):
    image_name = "mole2"
    docker_run_kwargs = {
        "volumes": {
            os.path.abspath(ROOT_DIR / "data/docker/mole2"): {"bind": "/data", "mode": "rw"},
        }
    }

    def _get_cmd_params(self, *, token: uuid.UUID, **_) -> str:
        return f"/data/{token}/in/mole_input.xml"

    async def _preprocess(self, *, token: str, input_files: list[str], **mole_data) -> None:
        await super()._preprocess(token=token, input_files=input_files)
        os.makedirs(ROOT_DIR / f"data/docker/{self.image_name}/{token}/out", exist_ok=True)
        os.makedirs(ROOT_DIR / f"data/docker/{self.image_name}/{token}/zip", exist_ok=True)
        self.build_xml_from_data(
            token=token,
            input_path=f"/data/{token}/in/{input_files[0]}",
            output_path=f"/data/{token}/out",
            data=MoleDto.model_validate(mole_data),
        )

    async def _postprocess(self, *, _output: str, token: uuid.UUID, **_) -> tuple[dict, list[str]]:
        calculation_dir = ROOT_DIR / f"data/docker/{self.image_name}/{token}"
        folder_to_zip = os.path.join(calculation_dir, "zip")
        zip_file = self.zip_folder_content(calculation_dir, "mole2_result.zip")
        [zip_hash] = [file_dto async for file_dto in self._file_storage_service.upload_files([zip_file], folder_to_zip)]
        return {"mole2_output": _output}, [zip_hash.file_name_hash]

    @staticmethod
    def zip_folder_content(folder_path: str, zip_name: str) -> str:
        folder_to_zip = os.path.join(folder_path, "zip")
        output_path = os.path.join(folder_to_zip, zip_name.removesuffix(".zip"))
        shutil.make_archive(output_path, "zip", root_dir=os.path.join(folder_path, "out"), base_dir=".")
        return zip_name

    @staticmethod
    def build_xml_from_data(token: str, input_path: str, output_path: str, data: MoleDto) -> None:
        root = E.Tunnels(
            E.Input(input_path),
            E.WorkingDirectory(output_path),
            E.Params(
                E.Cavity(
                    IgnoreHETAtoms=to_str(data.cavity.ignore_het_atoms),
                    IgnoreHydrogens=to_str(data.cavity.ignore_hydrogens),
                    InteriorThreshold=to_str(data.cavity.interior_threshold),
                    MinDepth=to_str(data.cavity.min_depth),
                    MinDepthLength=to_str(data.cavity.min_depth_length),
                    ProbeRadius=to_str(data.cavity.probe_radius),
                ),
                E.Tunnel(
                    SurfaceCoverRadius=to_str(data.tunnel.surface_cover_radius),
                    OriginRadius=to_str(data.tunnel.origin_radius),
                    AutoOriginCoverRadius=to_str(data.tunnel.auto_origin_cover_radius),
                    MaxAutoOriginsPerCavity=to_str(data.tunnel.max_auto_origins_per_cavity),
                    MaxTunnelSimilarity=to_str(data.tunnel.max_tunnel_similarity),
                    MinPoreLength=to_str(data.tunnel.min_pore_length),
                    MinTunnelLength=to_str(data.tunnel.min_tunnel_length),
                    BottleneckRadius=to_str(data.tunnel.bottleneck_radius),
                    BottleneckTolerance=to_str(data.tunnel.bottleneck_tolerance),
                    FilterBoundaryLayers=to_str(data.tunnel.filter_boundary_layers),
                    UseCustomExitsOnly=to_str(data.tunnel.use_custom_exits_only),
                    WeightFunction=to_str(data.tunnel.weight_function),
                ),
            ),
            E.Export(
                E.Formats(
                    ChargeSurface=to_str(data.export_options.charge_surface),
                    Chimera=to_str(data.export_options.chimera),
                    CSV=to_str(data.export_options.create_csv),
                    JSON=to_str(data.export_options.create_json),
                    Mesh=to_str(data.export_options.mesh),
                    PDBProfile=to_str(data.export_options.pdb_profile),
                    PDBStructure=to_str(data.export_options.pdb_structure),
                    PyMol=to_str(data.export_options.pymol),
                    VMD=to_str(data.export_options.vmd),
                ),
                E.Mesh(
                    Compress=to_str(data.export_options.compress),
                    Density=to_str(data.export_options.density),
                ),
                E.PyMol(
                    SurfaceType=to_str(data.export_options.surface_type),
                    ChargePalette=to_str(data.export_options.charge_palette),
                ),
                E.Types(
                    Cavities=to_str(data.export_options.cavities),
                    PoresAuto=to_str(data.export_options.pores_auto),
                    PoresMerged=to_str(data.export_options.pores_merged),
                    PoresUser=to_str(data.export_options.pores_user),
                    Tunnels=to_str(data.export_options.tunnels),
                ),
            ),
            *(
                [
                    E.CustomExits(
                        *[
                            E.Exit(
                                *[
                                    E.Point(X=to_str(point.x), Y=to_str(point.y), Z=to_str(point.z))
                                    for point in mole_exit.points
                                ]
                            )
                            for mole_exit in data.custom_exits
                        ]
                    )
                ]
                if data.custom_exits
                else []
            ),
        )
        doc = etree.ElementTree(root)
        doc.write(
            ROOT_DIR / f"data/docker/mole2/{token}/in/mole_input.xml",
            pretty_print=True,
            xml_declaration=True,
            encoding="UTF-8",
        )
