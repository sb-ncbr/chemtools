from api.controllers.index_controller import IndexController, index_router
from api.controllers.io_controller import IOController, io_router
from api.controllers.charge_controller import ChargeController, charge_router

router_list = [index_router, io_router, charge_router]

__all__ = ["ChargeController", "IOController", "IndexController", "router_list"]
