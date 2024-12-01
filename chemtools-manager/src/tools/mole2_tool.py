import os

from lxml import etree
from lxml.builder import E

from tools import BaseDockerizedTool


class Mole2Tool(BaseDockerizedTool):
    image_name = "mole2"
    docker_run_kwargs = {
        "volumes": {os.path.abspath("../data/docker/mole2"): {"bind": "/data", "mode": "rw"}},
        "detach": False,
    }

    def get_cmd_params(self, token: str) -> str:
        in_path = os.path.abspath("/data/{token}/input.xml")
        return in_path

    def preprocess(self, token: str):
        super().preprocess(token=token)
        self.build_xml_from_data(token=token, input_path=f"./tests/1tqn.cif", output_path=f"/data/{token}")

    def get_error(self, msg):
        return f"Mole2 calculation failed: {msg}"

    @staticmethod
    def build_xml_from_data(token: str, input_path: str, output_path: str) -> str:
        root = E.Tunnels(
            E.Input(input_path),
            E.WorkingDirectory(output_path),
            E.Params(
                E.Cavity(ProbeRadius="3", InteriorThreshold="1.25"), E.Tunnel(SurfaceCoverRadius="10", OriginRadius="5")
            ),
            E.Export(
                E.Formats(Mesh="1", PyMol="1", CSV="1", PDBProfile="1", PDBStructure="1"),
                E.Types(Cavities="1", Tunnels="1"),
                E.Mesh(Density="1.33", Compress="1"),
                E.PyMol(PDBId="1TQN", SurfaceType="Surface"),
            ),
            E.Origins(
                E.Origin(E.Residue(Chain="A", SequenceNumber="308"), E.Residue(Chain="A", SequenceNumber="309")),
                Auto="0",
            ),
        )
        doc = etree.ElementTree(root)
        doc.write(f"../data/docker/mole2/{token}/input.xml", pretty_print=True)
        return etree.tostring(doc, pretty_print=True).decode("utf-8")
