import uuid
from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv

from dependency_injector.wiring import Provide, inject

from api.models import ChargeMethodsResponse
from clients import ChemtoolsManagerClient
from containers import ApplicationContainer
from api.models.charge import ChargeRequest


charge_router = APIRouter(tags=["Charge"])


@cbv(charge_router)
class ChargeController:
    @inject
    def __init__(
        self,
        chemtools_manager_client: ChemtoolsManagerClient = Depends(
            Provide[ApplicationContainer.chemtools_manager_client]
        ),
    ):
        self.__chemtools_manager_client = chemtools_manager_client

    @charge_router.post("/charge_calculation/")
    async def charge_calculation(self, data: ChargeRequest) -> ChargeMethodsResponse:
        response = await self.__chemtools_manager_client.chargefw2(data)
        return response
