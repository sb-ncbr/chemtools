import aiofiles
import os

from services import FileStorageService
from api.models import UploadRequest


class FilesystemStorageService(FileStorageService):
    _DATA_DIR = "../data/calculations"

    # NOTE there might be a filename collision when unzipping files from multiple zip files or
    # when uploading additional files with the same name
    async def upload_files(self, data: UploadRequest):
        os.makedirs(f"{self._DATA_DIR}/{data.token}", exist_ok=True)
        for request_file in data.files:
            if request_file.content_type == "application/zip":
                for file_name, file_func_wrapper in self.unzip_files(request_file.file).items():
                    async with aiofiles.open(f"{self._DATA_DIR}/{data.token}/{file_name}", "wb") as file:
                        res = file_func_wrapper()
                        await file.write(res)

            else:
                async with aiofiles.open(f"{self._DATA_DIR}/{data.token}/{request_file.filename}", "wb") as file:
                    await file.write(await request_file.read())

    async def fetch_files(self, token):
        pass
