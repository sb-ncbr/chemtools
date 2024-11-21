from api.controllers.system_controller import SystemController, system_router
from api.controllers.io_controller import IOController, io_router
from api.controllers.charge_controller import ChargeController, charge_router

router_list = [system_router, io_router, charge_router]

__all__ = ["router_list", "ChargeController", "IOController", "SystemController"]
