import os
from collections import Counter, defaultdict
import uuid

from api.enums import ChargeModeEnum
from tools import BaseDockerizedTool


class ChargeFW2Tool(BaseDockerizedTool):
    image_name = "chargefw2"
    docker_run_kwargs = {"volumes": {os.path.abspath("../data/docker/chargefw2"): {"bind": "/data", "mode": "rw"}}}

    def _get_cmd_params(
        self,
        input_file: str,
        mode: ChargeModeEnum,
        token: str = '',
        ignore_water: bool = False,
        read_hetatm: bool = False,
        permissive_types: bool = False,
        method: str = '',
        parameter: str = '',
        **_,
    ) -> str:
        in_path = os.path.abspath(f"/data/in/{input_file}")
        out_path = os.path.abspath(f"/data/out/{token}")

        base_args = f"--mode {mode} --input-file {in_path}"
        out_param = f" --chg-out-dir {out_path}" if mode == ChargeModeEnum.charges else ""
        flags = f"{' --ignore-water' if ignore_water else ''}{' --read-hetatm' if read_hetatm else ''}{' --permissive-types' if permissive_types else ''}"
        parameters = f"{f' --method {method}' if method else ''}{f' --par-file {parameter}' if parameter else ''}"
        return f"{base_args}{out_param}{flags}{parameters}"

    async def _preprocess(self, **kwargs) -> uuid.UUID:
        token = await super()._preprocess(**kwargs)
        if token is not None:
            os.makedirs(f"../data/docker/chargefw2/out/{token}", exist_ok=True)
        return token

    async def _postprocess(
        self, *, _output: str, input_file: str, token: uuid.UUID = None, mode: ChargeModeEnum, **kwargs
    ) -> str:
        if mode == ChargeModeEnum.charges:
            file_names = os.listdir(f"../data/docker/chargefw2/out/{token}")
            all_suffixes = {file_name.split(".")[-1] for file_name in file_names}
            file_token = f"{input_file.split('.')[0]}"
            response_files = {suffix: f"{file_token}.{suffix}" for suffix in all_suffixes} | {
                "cif": {file_name.split(".")[0]: file_name for file_name in file_names if file_name.endswith(".cif")},
            }
            all_suffixes.discard("cif")
            await self._push_output_files(
                token,
                [response_files[suffix].removesuffix(f".{suffix}") + f".sdf.{suffix}" for suffix in all_suffixes]
                + list(response_files["cif"].values()),
            )
            return response_files
        return _output

    def _get_error(self, msg):
        return f"ChargeFW2 calculation failed: {msg}"

    @staticmethod
    def calculate_suitable_methods(calculation: str) -> tuple[list[str], dict[str, list[str]]]:
        suitable_methods = Counter()

        for line in calculation.splitlines():
            if not line.strip():
                continue

            method, *parameters = line.strip().split()
            if not parameters:
                suitable_methods[(method,)] += 1
                continue

            for p in parameters:
                suitable_methods[(method, p)] += 1

        # TODO is this line necessary?
        # ok, this needs to filter out methods which are not applicable to every file
        # (only if we support multiple files simultaneously)
        suitable_methods = {k: v for k, v in suitable_methods.items() if v == 1}

        methods = list({method for method, *_ in suitable_methods})

        parameters = defaultdict(list)
        for pair in suitable_methods:
            if len(pair) == 2:
                parameters[pair[0]].append(pair[1])

        return methods, parameters

    @staticmethod
    def parse_info_output(output: str) -> dict:
        molecules_count_line, atoms_count_line, *atom_lines = output.strip().splitlines()
        data = {
            "number_of_molecules": int(molecules_count_line.split(":")[1]),
            "number_of_atoms": int(atoms_count_line.split(":")[1]),
        }

        atom_counts = {}
        for line in atom_lines:
            atom_type, atom_count = line.split("*")
            atom_counts[atom_type.strip()] = int(atom_count.split(":")[1])

        return {**data, "atom_counts": atom_counts}
