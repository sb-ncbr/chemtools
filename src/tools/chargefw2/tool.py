import os
import re
import uuid
from collections import Counter, defaultdict

from api.schemas.user_file import UserFileDto
from conf.const import ROOT_DIR
from tools.chargefw2.schema import (
    ChargeBestParametersResponseDto,
    ChargeInfoResponseDto,
    ChargeModeEnum,
    ChargeResponseDto,
    ChargeSuitableMethodsResponseDto,
)
from tools.dockerized_tool_base import DockerizedToolBase


class ChargeFW2Tool(DockerizedToolBase):
    image_name = "chargefw2"
    docker_run_kwargs = {"volumes": {ROOT_DIR / "data/docker/chargefw2": {"bind": "/data", "mode": "rw"}}}

    def _get_cmd_params(
        self,
        _token: uuid.UUID,
        _input_files: list[str],
        mode: ChargeModeEnum,
        ignore_water: bool = False,
        read_hetatm: bool = False,
        permissive_types: bool = False,
        method: str = "",
        parameter: str = "",
        **_,
    ) -> str:
        in_path = os.path.abspath(f"/data/{_token}/in/{_input_files[0]}")
        out_path = os.path.abspath(f"/data/{_token}/out")

        base_args = f"--mode {mode} --input-file {in_path}"
        out_param = f" --chg-out-dir {out_path}" if mode == ChargeModeEnum.charges else ""
        flags = (
            f"{' --ignore-water' if ignore_water else ''}"
            f"{' --read-hetatm' if read_hetatm else ''}"
            f"{' --permissive-types' if permissive_types else ''}"
        )
        parameters = f"{f' --method {method}' if method else ''}{f' --par-file {parameter}' if parameter else ''}"
        return f"{base_args}{out_param}{flags}{parameters}"

    async def _preprocess(self, _token: uuid.UUID, _input_files: list[str], mode: ChargeModeEnum, **_) -> None:
        if mode == ChargeModeEnum.charges:
            os.makedirs(ROOT_DIR / f"data/docker/{self.image_name}/{_token}/out", exist_ok=True)
        await super()._preprocess(_token=_token, _input_files=_input_files)

    async def _postprocess(
        self, *, _output: str, _token: uuid.UUID, mode: ChargeModeEnum, **_
    ) -> tuple[dict, list[str]]:
        if mode == ChargeModeEnum.info:
            parsed_data = self.parse_info_output(_output)
            return ChargeInfoResponseDto(**parsed_data).model_dump(), []

        elif mode == ChargeModeEnum.charges:
            file_names = os.listdir(ROOT_DIR / f"data/docker/{self.image_name}/{_token}/out")
            user_file_dtos = await self._send_files(token=_token, file_names=file_names)
            files_data = self.get_file_data(user_file_dtos)
            file_hashes = [file_obj.file_name_hash for file_obj in user_file_dtos]
            return ChargeResponseDto(**files_data).model_dump(), file_hashes

        elif mode == ChargeModeEnum.suitable_methods:
            methods, parameters = self.calculate_suitable_methods(_output)
            return ChargeSuitableMethodsResponseDto(methods=methods, parameters=parameters).model_dump(), []

        elif mode == ChargeModeEnum.best_parameters:
            best_params = self.parse_best_params(_output)
            return ChargeBestParametersResponseDto(best_parameters=best_params).model_dump(), []

        else:
            raise NotImplementedError(f"Mode {mode} is not implemented for chargefw2 tool")

    @staticmethod
    def get_file_data(user_file_dtos: list[UserFileDto]) -> tuple[dict[str, str], list[str]]:
        all_suffixes = {file_dto.file_name.split(".")[-1] for file_dto in user_file_dtos}
        return {
            suffix: {
                user_file_dto.file_name: user_file_dto.file_name_hash
                for user_file_dto in user_file_dtos
                if user_file_dto.file_name.endswith(suffix)
            }
            for suffix in all_suffixes
        }

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

    @staticmethod
    def parse_best_params(output: str) -> str | None:
        match = re.fullmatch(r"Best parameters are: (\S+)\.json\n", output)
        return match.group(1) if match else None
