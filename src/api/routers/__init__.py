from api.routers.calculations_router import CalculationsRouter, calculations_router
from api.routers.io_router import IORouter, io_router
from api.routers.system_router import SystemRouter, system_router
from api.routers.tools_router import ToolsRouter, tools_router
from api.routers.users_router import UsersRouter, users_router

router_list = [system_router, io_router, tools_router, calculations_router, users_router]

__all__ = [
    "CalculationsRouter",
    "IORouter",
    "SystemRouter",
    "ToolsRouter",
    "UsersRouter",
    "router_list",
]
