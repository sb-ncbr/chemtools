import os
import re

from conf.const import ROOT_DIR
from tools.dockerized_tool_base import DockerizedToolBase


class GesamtTool(DockerizedToolBase):
    image_name = "gesamt"
    docker_run_kwargs = {"volumes": {os.path.abspath(ROOT_DIR / "data/docker/gesamt"): {"bind": "/data", "mode": "r"}}}

    def _get_cmd_params(self, *, token: str, input_files: list[str], selection_strings: list[str], **_) -> str:
        result = " ".join(
            (f"-d {selection_string} " if selection_string is not None else "")
            + os.path.abspath(f"/data/{token}/in/{file_name}")
            for file_name, selection_string in zip(input_files, selection_strings)
        )
        return result

    async def _postprocess(self, *, input_files: list[str], _output: str, **_) -> tuple[dict, list[str]]:
        if len(input_files) == 2:
            return self.parse_output_two_files(_output), []
        return self.parse_output_more_than_three_files(_output), []

    @staticmethod
    def parse_output_two_files(_output: str) -> dict:
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

    @staticmethod
    def parse_output_more_than_three_files(_output: str) -> dict:
        # TODO please finish this someone more competent
        return {}
