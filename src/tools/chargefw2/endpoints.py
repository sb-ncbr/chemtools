from tools.chargefw2.schema import ChargeInfoRequestDto, ChargeModeEnum, ChargeRequestDto

endpoints = {
    "/chargefw2/info": ("charge_info", ChargeInfoRequestDto, {"mode": ChargeModeEnum.info}),
    "/chargefw2/charges": ("charge_charges", ChargeRequestDto, {"mode": ChargeModeEnum.charges}),
    "/chargefw2/suitable-methods": (
        "charge_suitable_methods",
        ChargeRequestDto,
        {"mode": ChargeModeEnum.suitable_methods},
    ),
    "/chargefw2/best-parameters": (
        "charge_best_parameters",
        ChargeRequestDto,
        {"mode": ChargeModeEnum.best_parameters},
    ),
}
