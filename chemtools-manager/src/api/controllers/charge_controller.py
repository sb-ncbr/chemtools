import uuid
from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv

from dependency_injector.wiring import Provide, inject

from api.models import ChargeMethodsResponse, ChargeRequest
from containers import ApplicationContainer
from tools import ChargeFW2Tool


charge_router = APIRouter(tags=["Charge"])


@cbv(charge_router)
class ChargeController:
    @inject
    def __init__(
        self,
        chargefw2_tool: ChargeFW2Tool = Depends(Provide[ApplicationContainer.chargefw2_tool]),
    ):
        self.__chargefw2_tool = chargefw2_tool

    @charge_router.post("/chargefw2/")
    async def charge_calculation(
        self,
        data: ChargeRequest,
    ) -> ChargeMethodsResponse:
        calculation_token = str(uuid.uuid4())
        # TODO make this async
        chargefw2_output = self.__chargefw2_tool.run(data.mode, token=calculation_token)
        suitable_methods = self.__chargefw2_tool.calculate_suitable_methods(chargefw2_output)
        # uuid_str = str(uuid.uuid4())
        return suitable_methods
