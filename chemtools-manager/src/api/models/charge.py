import uuid
from pydantic import BaseModel

from api.enums import ChargeModeEnum


class ChargeMethodsResponse(BaseModel):
    methods: list[str]
    parameters: dict[str, list[str]]


class ChargeRequest(BaseModel):
    token: uuid.UUID
    mode: ChargeModeEnum
    file_names: list[str]
