import os
import re

from api.schemas.gesamt import GesamtResponseDto
from tools import BaseDockerizedTool


class GesamtTool(BaseDockerizedTool):
    image_name = "gesamt"
    docker_run_kwargs = {"volumes": {os.path.abspath("../data/docker/gesamt"): {"bind": "/data", "mode": "rw"}}}

    def _get_cmd_params(self, input_files: list[str], *args, **kwargs) -> str:
        return " ".join([os.path.abspath(f'/data/in/{file_name}') for file_name in input_files])

    async def _postprocess(self, *, _output: str, **_) -> dict:
        lines = _output.splitlines()
        matrix_start_idx = lines.index(" Transformation matrix for MOVING structure:") + 3
        matrix = list(zip(*[line.split() for line in lines[matrix_start_idx : matrix_start_idx + 3]]))

        return {
            "q_score": re.search(r"Q-score\s+:\s+([\d.]+)", _output).group(1),
            "rmsd": re.search(r"RMSD\s+:\s+([\d.]+)", _output).group(1),
            "aligned_residues": re.search(r"Aligned residues\s+:\s+(\d+)", _output).group(1),
            "sequence_id": re.search(r"Sequence Id:\s+:\s+([\d.]+)", _output).group(1),
            "translation_vector": matrix.pop(),
            "rotation_matrix": [row for row in zip(*matrix)],
        }

    def _get_error(self, msg):
        return f"Gesamt calculation failed: {msg}"
