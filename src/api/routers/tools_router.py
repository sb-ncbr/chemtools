import logging

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Request
from fastapi_utils.cbv import cbv

from api.schemas.calculation import CreateCalculationRequestDto, TaskInfoResponseDto
from containers import AppContainer
from services.calculation_service import CalculationService
from tools.chargefw2.schema import ChargeModeEnum
from utils import get_tool_modules

logger = logging.getLogger(__name__)

tools_router = APIRouter(tags=["Tools"])


class ToolsRouter:
    @inject
    def __init__(self, calculation_service: CalculationService = Depends(Provide[AppContainer.calculation_service])):
        self.calculation_service = calculation_service

    @tools_router.get("/chargefw2")
    async def chargefw2(self) -> dict[str, list[ChargeModeEnum]]:
        return {"available_modes": list(ChargeModeEnum)}


for tool_name, tool_module in get_tool_modules("endpoints"):
    if not hasattr(tool_module, "endpoints"):
        raise NotImplementedError(f"Package tools.{tool_name} does not have 'endpoints' module.")

    for endpoint, (endpoint_name, data_type, additional_attrs) in tool_module.endpoints.items():

        def wrapper(tool_name=tool_name, additional_attrs=additional_attrs):
            async def endpoint_func(self, request, data):
                return await self.calculation_service.create_calculation(request, tool_name, data, **additional_attrs)

            return endpoint_func

        endpoint_func = wrapper()
        endpoint_func.__name__ = endpoint_name
        endpoint_func.__annotations__ = {
            "request": Request,
            "data": CreateCalculationRequestDto[data_type],
            "return": TaskInfoResponseDto,
        }

        endpoint_func.__module__ = "api.routers.tools_router"

        setattr(
            ToolsRouter,
            endpoint_name,
            endpoint_func,
        )
        tools_router.post(endpoint)(endpoint_func)

ToolsRouter = cbv(tools_router)(ToolsRouter)
