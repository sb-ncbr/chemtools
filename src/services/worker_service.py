import logging
from datetime import UTC, datetime

from api.enums import DockerizedToolEnum
from api.schemas.calculation import CalculationRequestDto
from db.models.calculation import CalculationResultModel, CalculationStatusEnum
from db.repos.calculation_request_repo import CalculationRequestRepo
from db.repos.calculation_result_repo import CalculationResultRepo
from tools.base_dockerized_tool import BaseDockerizedTool, ContainerRuntimeError
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

    def get_dockerized_tool(self, _tool_name: DockerizedToolEnum) -> BaseDockerizedTool:
        tool = {
            DockerizedToolEnum.chargefw2: self.chargefw2_tool,
            DockerizedToolEnum.mole2: self.mole2_tool,
            DockerizedToolEnum.gesamt: self.gesamt_tool,
        }.get(_tool_name)

        if not tool:
            raise NotImplementedError(f"Tool class not found for {_tool_name}")

        return tool

    async def run_calculation_async(self, **data) -> None:
        logger.info(f"Received message: {data}")
        calculation_dto = CalculationRequestDto.model_validate(data)
        calculation = await self.calculation_request_repo.get_by(id=calculation_dto.id)
        await self.calculation_request_repo.update(
            calculation,
            tool_name=calculation_dto.tool_name,
            status=CalculationStatusEnum.running,
        )

        dockerized_tool = self.get_dockerized_tool(calculation_dto.tool_name)
        logger.info(f"Running '{dockerized_tool.image_name}' tool by user={calculation_dto.user_id}")
        status = CalculationStatusEnum.success
        time_started = datetime.now(UTC)
        try:
            result = await dockerized_tool.run(
                token=calculation_dto.id,
                input_files=calculation_dto.input_files,
                user_id=calculation_dto.user_id,
                **calculation_dto.input_data,
            )
        except Exception as e:
            error_log = (
                f"Tool '{dockerized_tool.image_name}' run by user={calculation_dto.user_id} failed with error: {e}"
            )
            if isinstance(e, ContainerRuntimeError):
                logger.warning(error_log)
            else:
                logger.exception(error_log)
            result = str(e)
            status = CalculationStatusEnum.failure

        calculation_result = await self.calculation_result_repo.create(
            CalculationResultModel(
                output_files=[],
                output_data=result,
                started_at=time_started,
                finished_at=datetime.now(UTC),
            )
        )
        await self.calculation_request_repo.update(calculation, calculation_result=calculation_result, status=status)
