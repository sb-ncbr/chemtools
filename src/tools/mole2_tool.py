import os

from lxml import etree
from lxml.builder import E

from api.schemas.mole import MoleRequestDto
from conf.const import ROOT_DIR
from tools import BaseDockerizedTool


class Mole2Tool(BaseDockerizedTool):
    image_name = "mole2"
    docker_run_kwargs = {
        "volumes": {
            os.path.abspath(ROOT_DIR / "data/docker/mole2"): {"bind": "/data", "mode": "rw"},
        }
    }

    def _get_cmd_params(self, *args, **kwargs) -> str:
        in_path = os.path.abspath("/data/{token}/input.xml")
        return in_path

    async def _preprocess(self, token: str, data: MoleRequestDto):
        await super()._preprocess()
        self.build_xml_from_data(
            token=token, input_path="/input_data/asdf/1tqn.cif", output_path=f"/data/{token}", data=data
        )

    @staticmethod
    def build_xml_from_data(token: str, input_path: str, output_path: str, data: MoleRequestDto) -> None:
        root = E.Tunnels(
            E.Input(input_path),
            E.WorkingDirectory(output_path),
            E.Params(
                E.Cavity(
                    IgnoreHetAtoms=data.cavity.ignore_het_atoms,
                    IgnoreHydrogens=data.cavity.ignore_hydrogens,
                    InteriorThreshold=data.cavity.interior_threshold,
                    MinDepth=data.cavity.min_depth,
                    MinDepthLength=data.cavity.min_depth_length,
                    ProbeRadius=data.cavity.probe_radius,
                ),
                E.Tunnel(
                    SurfaceCoverRadius=data.tunnel.surface_cover_radius,
                    OriginRadius=data.tunnel.origin_radius,
                    AutoOriginCoverRadius=data.tunnel.auto_origin_cover_radius,
                    MaxAutoOriginsPerCavity=data.tunnel.max_auto_origins_per_cavity,
                    MaxTunnelSimilarity=data.tunnel.max_tunnel_similarity,
                    MinPoreLength=data.tunnel.min_pore_length,
                    MinTunnelLength=data.tunnel.min_tunnel_length,
                    BottleneckRadius=data.tunnel.bottleneck_radius,
                    BottleneckTolerance=data.tunnel.bottleneck_tolerance,
                    FilterBoundaryLayers=data.tunnel.filter_boundary_layers,
                    UseCustomExitsOnly=data.tunnel.use_custom_exits_only,
                    WeightFunction=data.tunnel.weight_function,
                ),
            ),
            E.Export(
                E.Formats(
                    ChargeSurface=data.export_options.charge_surface,
                    Chimera=data.export_options.chimera,
                    CSV=data.export_options.create_csv,
                    JSON=data.export_options.create_json,
                    Mesh=data.export_options.mesh,
                    PDBProfile=data.export_options.pdb_profile,
                    PDBStructure=data.export_options.pdb_structure,
                    PyMol=data.export_options.pymol,
                    VMD=data.export_options.vmd,
                ),
                E.Mesh(Compress=data.export_options.compress, Density=data.export_options.density),
                E.PyMol(SurfaceType=data.export_options.surface_type, ChargePalette=data.export_options.charge_palette),
                E.Types(
                    Cavities=data.export_options.cavities,
                    PoresAuto=data.export_options.pores_auto,
                    PoresMerged=data.export_options.pores_merged,
                    PoresUser=data.export_options.pores_user,
                    Tunnels=data.export_options.tunnels,
                ),
            ),
            *(
                [
                    E.CustomExits(
                        *[
                            E.Exit(*[E.Point(**point.model_dump()) for point in mole_exit.points])
                            for mole_exit in data.custom_exits
                        ]
                    )
                ]
                if data.custom_exits
                else []
            ),
            E.Origins(
                E.Origin(E.Residue(Chain="A", SequenceNumber="308"), E.Residue(Chain="A", SequenceNumber="309")),
                Auto="0",
            ),
        )
        doc = etree.ElementTree(root)
        doc.write(ROOT_DIR / f"data/docker/mole2/{token}/input.xml", pretty_print=True)
