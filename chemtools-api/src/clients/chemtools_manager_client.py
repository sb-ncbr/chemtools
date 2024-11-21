from clients import BaseClient
from api.models import ChargeRequest, UploadRequest


class ChemtoolsManagerClient(BaseClient):
    async def chargefw2(self, data: ChargeRequest):
        return await self._post("/chargefw2/", data=data.model_dump_json())

    async def upload_files(self, data: UploadRequest):
        file_data = [("files", (file.filename, file.file, file.content_type)) for file in data.files]
        return await self._post("/upload_files/", data={"token": str(data.token)}, files=file_data)
