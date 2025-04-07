import logging
from datetime import UTC, datetime

from api.schemas.calculation import CalculationRequestDto
from db.models.calculation import CalculationResultModel, CalculationStatusEnum
from db.repos.calculation_request_repo import CalculationRequestRepo
from db.repos.calculation_result_repo import CalculationResultRepo
from tools.dockerized_tool_base import DockerizedToolBase

logger = logging.getLogger(__name__)


class WorkerService:
    def __init__(
        self,
        calculation_request_repo: CalculationRequestRepo,
        calculation_result_repo: CalculationResultRepo,
        **tools: DockerizedToolBase,
    ):
        self.calculation_request_repo = calculation_request_repo
        self.calculation_result_repo = calculation_result_repo
        self.tools = {}
        for tool_name_attr, tool_obj in tools.items():
            setattr(self, tool_name_attr, tool_obj)
            self.tools[tool_name_attr.removesuffix("_tool")] = tool_obj

    async def run_calculation_async(self, **data) -> None:
        logger.info(f"Received message: {data}")

        calculation_dto = CalculationRequestDto.model_validate(data)
        calculation = await self.calculation_request_repo.get_by(id=calculation_dto.id)
        await self.calculation_request_repo.update(calculation, status=CalculationStatusEnum.running)

        dockerized_tool = self.tools.get(calculation_dto.tool_name)
        if not dockerized_tool:
            raise NotImplementedError(f"Tool {dockerized_tool} not implemented")

        time_started = datetime.now(UTC)
        status, output_data, output_files = await self._run_container(dockerized_tool, calculation_dto)

        await self._save_calculation_result(calculation, status, output_data, output_files, time_started)

    async def _run_container(self, dockerized_tool: DockerizedToolBase, calculation_dto: CalculationRequestDto) -> None:
        logger.info(f"Running '{dockerized_tool.image_name}' tool by user={calculation_dto.user_id}")
        try:
            result, output_files = await dockerized_tool.run(
                token=calculation_dto.id,
                input_files=calculation_dto.input_files,
                user_id=calculation_dto.user_id,
                **calculation_dto.input_data,
            )
            return CalculationStatusEnum.success, result, output_files
        except Exception as e:
            logger.exception(
                f"Tool '{dockerized_tool.image_name}' run by user={calculation_dto.user_id} failed with error: {e}"
            )
            return CalculationStatusEnum.failure, {"error": str(e)}, []

    async def _save_calculation_result(
        self,
        calculation: CalculationRequestDto,
        status: CalculationStatusEnum,
        output_data: str,
        output_files: list[str],
        time_started: datetime,
    ) -> None:
        calculation_result = await self.calculation_result_repo.create(
            CalculationResultModel(
                output_files=output_files,
                output_data=output_data,
                duration=(datetime.now(UTC) - time_started).total_seconds(),
            )
        )
        await self.calculation_request_repo.update(calculation, calculation_result=calculation_result, status=status)
