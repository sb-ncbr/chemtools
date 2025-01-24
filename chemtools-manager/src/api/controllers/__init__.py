from api.controllers.io_controller import IOController, io_router
from api.controllers.system_controller import SystemController, system_router
from api.controllers.tools_controller import ToolsController, tools_router

router_list = [system_router, io_router, tools_router]

__all__ = [
    "router_list",
    "SystemController",
    "IOController",
    "ToolsController",
]
