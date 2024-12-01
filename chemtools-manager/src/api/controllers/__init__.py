from api.controllers.system_controller import SystemController, system_router
from api.controllers.io_controller import IOController, io_router
from api.controllers.charges_controller import ChargesController, charges_router
from api.controllers.tunnels_controller import TunnelsController, tunnels_router

router_list = [system_router, io_router, charges_router, tunnels_router]

__all__ = ["router_list", "ChargesController", "TunnelsController", "SystemController", "IOController"]
