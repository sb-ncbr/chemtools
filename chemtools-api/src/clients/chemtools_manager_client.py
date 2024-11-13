import json
from clients import BaseClient
from api.models.charge import ChargeRequest


class ChemtoolsManagerClient(BaseClient):
    async def chargefw2(self, data: ChargeRequest):
        data = data.model_dump_json()
        return await self._post("/chargefw2/", json.loads(data))
