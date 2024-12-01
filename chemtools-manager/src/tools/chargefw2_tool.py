from collections import Counter, defaultdict
import os

from api.enums import ChargeModeEnum
from api.models.charge import ChargeMethodsResponse
from tools import BaseDockerizedTool


class ChargeFW2Tool(BaseDockerizedTool):
    image_name = "chargefw2"
    docker_run_kwargs = {
        "volumes": {os.path.abspath("../data/docker/chargefw2"): {"bind": "/data", "mode": "rw"}},
        "detach": False,
    }

    def get_cmd_params(self, mode: ChargeModeEnum, token: str) -> str:
        in_path = os.path.abspath("/data/molecules.sdf")
        out_path = os.path.abspath(f"/data/{token}")
        return {
            ChargeModeEnum.charges: f"--mode {mode} --input-file {in_path} --chg-out-dir {out_path}",
            ChargeModeEnum.suitable_methods: f"--mode {mode} --input-file {in_path} --read-hetatm --permissive-types",
        }.get(mode, "--help")

    def postprocess(self, *args, _output: bytes, **kwargs):
        print(_output, args, kwargs)
        return super().postprocess(*args, _output=_output, **kwargs)

    def get_error(self, msg):
        return f"ChargeFW2 calculation failed: {msg}"

    @staticmethod
    def calculate_suitable_methods(calculation: str) -> ChargeMethodsResponse:
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

        return ChargeMethodsResponse(methods=methods, parameters=parameters)
