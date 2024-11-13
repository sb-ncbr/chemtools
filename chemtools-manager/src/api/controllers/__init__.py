from api.controllers.charge_controller import ChargeController, charge_router
from api.controllers.index_controller import IndexController, index_router

router_list = [index_router, charge_router]

__all__ = ["ChargeController", "IndexController", "router_list"]
