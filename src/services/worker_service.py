import logging
from datetime import UTC, datetime

from api.enums import DockerizedToolEnum
from api.schemas.calculation import CalculationRequestDto
from db.models.calculation import CalculationResultModel, CalculationStatusEnum
from db.repos.calculation_request_repo import CalculationRequestRepo
from db.repos.calculation_result_repo import CalculationResultRepo
from tools.base_dockerized_tool import BaseDockerizedTool
from tools.chargefw2_tool import ChargeFW2Tool
from tools.gesamt_tool import GesamtTool
from tools.mole2_tool import Mole2Tool

logger = logging.getLogger(__name__)


class WorkerService:
    def __init__(
        self,
        chargefw2_tool: ChargeFW2Tool,
        mole2_tool: Mole2Tool,
        gesamt_tool: GesamtTool,
        calculation_request_repo: CalculationRequestRepo,
        calculation_result_repo: CalculationResultRepo,
    ):
        self.chargefw2_tool = chargefw2_tool
        self.mole2_tool = mole2_tool
        self.gesamt_tool = gesamt_tool
        self.calculation_request_repo = calculation_request_repo
        self.calculation_result_repo = calculation_result_repo

    async def run_calculation_async(self, **data) -> None:
        logger.info(f"Received message: {data}")

        calculation_dto = CalculationRequestDto.model_validate(data)
        calculation = await self.calculation_request_repo.get_by(id=calculation_dto.id)
        await self.calculation_request_repo.update(calculation, status=CalculationStatusEnum.running)

        dockerized_tool = self._get_dockerized_tool(calculation_dto.tool_name)
        time_started = datetime.now(UTC)
        status, output_data, output_files = await self._run_container(dockerized_tool, calculation_dto)

        await self._save_calculation_result(calculation, status, output_data, output_files, time_started)

    def _get_dockerized_tool(self, _tool_name: DockerizedToolEnum) -> BaseDockerizedTool:
        tool = {
            DockerizedToolEnum.chargefw2: self.chargefw2_tool,
            DockerizedToolEnum.mole2: self.mole2_tool,
            DockerizedToolEnum.gesamt: self.gesamt_tool,
        }.get(_tool_name)

        if not tool:
            raise NotImplementedError(f"Tool class not found for {_tool_name}")

        return tool

    async def _run_container(self, dockerized_tool: BaseDockerizedTool, calculation_dto: CalculationRequestDto) -> None:
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
            logger.error(
                f"Tool '{dockerized_tool.image_name}' run by user={calculation_dto.user_id} failed with error: {e}"
            )
            return CalculationStatusEnum.failure, str(e), []

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
                started_at=time_started,
                finished_at=datetime.now(UTC),
            )
        )
        await self.calculation_request_repo.update(calculation, calculation_result=calculation_result, status=status)
