import os
import re

from api.schemas.gesamt import GesamtInputDto
from conf.const import ROOT_DIR
from tools import BaseDockerizedTool


class GesamtTool(BaseDockerizedTool):
    image_name = "gesamt"
    docker_run_kwargs = {"volumes": {os.path.abspath(ROOT_DIR / "data/docker/gesamt"): {"bind": "/data", "mode": "rw"}}}

    def _get_cmd_params(self, *, input_data: list[GesamtInputDto], **kwargs) -> str:
        result = " ".join(
            (f"-d {file.selection_string} " if file.selection_string is not None else "")
            + os.path.abspath(f"/data/in/{file.file_name}")
            for file in input_data
        )
        return result

    async def _postprocess(self, *, input_data: list[GesamtInputDto], _output: str, **_) -> dict:
        if len(input_data) == 2:
            return self.__parse_output_2_files(_output)
        return self.__parse_output_more_files(_output)

    def _get_error(self, msg):
        return f"Gesamt calculation failed: {msg}"

    @staticmethod
    def __parse_output_2_files(_output: str):
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
    def __parse_output_more_files(_output: str):
        return {}
