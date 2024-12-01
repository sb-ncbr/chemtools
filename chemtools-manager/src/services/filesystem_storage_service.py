import uuid
import aiofiles
import os

from fastapi import HTTPException

from services import FileStorageService
from api.models import UploadRequest


class FilesystemStorageService(FileStorageService):
    _DATA_DIR = "../data/calculations"

    # NOTE there might be a filename collision when unzipping files from multiple zip files or
    # when uploading additional files with the same name
    async def upload_files(self, data: UploadRequest) -> uuid.UUID:
        token = uuid.uuid4()
        os.makedirs(f"{self._DATA_DIR}/{token}", exist_ok=True)
        for request_file in data.files:
            if request_file.content_type == "application/zip":
                for file_name, file_func_wrapper in self.unzip_files(request_file.file).items():
                    await self.save_file(
                        token=token, file_name=file_name, file_bytes=file_func_wrapper(), make_dir=False
                    )

            else:
                await self.save_file(
                    token=token,
                    file_name=request_file.filename,
                    file_bytes=await request_file.read(),
                    make_dir=False,
                )

        return token

    # NOTE if there is a directory, it fails
    async def save_file(self, token: uuid.UUID, file_name: str, file_bytes: bytes, make_dir=True) -> None:
        if make_dir:
            os.makedirs(f"{self._DATA_DIR}/{token}", exist_ok=True)
        try:
            async with aiofiles.open(f"{self._DATA_DIR}/{token}/{file_name}", "wb") as file:
                await file.write(file_bytes)
        except FileNotFoundError:
            raise HTTPException(
                status_code=400, detail=f"Unable to save file {file_name}. Zip file maybe contains directories?"
            )
        except Exception as e:
            self._logger.error(f"Error while saving file {file_name}: {e}")
            raise HTTPException(status_code=400, detail=f"Unable to save file {file_name}.")

    async def fetch_files(self, token):
        pass
