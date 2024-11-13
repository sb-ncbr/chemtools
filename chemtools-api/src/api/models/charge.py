import uuid

from pydantic import BaseModel

from api.enums import ChargeModeEnum


class ChargeResponse(BaseModel):
    token: uuid.UUID


class ChargeRequest(BaseModel):
    token: uuid.UUID
    mode: ChargeModeEnum
    file_names: list[str]


class ChargeMethodsResponse(BaseModel):
    methods: list[str]
    parameters: dict[str, list[str]]
