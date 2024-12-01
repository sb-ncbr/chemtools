import uuid
from fastapi import APIRouter
from fastapi_utils.cbv import cbv

from dependency_injector.wiring import inject

from tools import Mole2Tool
from utils import from_app_container

tunnels_router = APIRouter(tags=["Tunnels"])


@cbv(tunnels_router)
class TunnelsController:
    @inject
    def __init__(
        self,
        mole2_tool: Mole2Tool = from_app_container("mole2_tool"),
    ):
        self.__mole2_tool = mole2_tool

    @tunnels_router.post("/mole2/")
    async def mole_calculation(self) -> dict:
        calculation_token = str(uuid.uuid4())
        self.__mole2_tool.run(token=calculation_token)
        return {"status": "ok"}
