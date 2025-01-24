import os
import uuid
from typing import TYPE_CHECKING

import aiofiles
from fastapi import HTTPException

from api.schemas.upload import UploadRequestDto
from services import FileStorageService

if TYPE_CHECKING:
    pass


class FilesystemStorageService(FileStorageService):
    _DATA_DIR = "../data/file_storage"

    def __init__(self, *args, **kwargs):
        if not os.path.exists(self._DATA_DIR):
            os.makedirs(self._DATA_DIR)
        super().__init__(*args, **kwargs)

    # NOTE there might be a filename collision when unzipping files from multiple zip files or
    # when uploading additional files with the same name
    async def upload_files(self, data: UploadRequestDto) -> list[uuid.UUID]:
        created_tokens = []
        for request_file in data.files:
            if request_file.content_type == "application/zip":
                for file_name, file_func_wrapper in self.unzip_files(request_file.file).items():
                    token = await self.save_file(file_name=file_name, file_bytes=file_func_wrapper())
                    created_tokens.append(token)

            else:
                token = await self.save_file(
                    file_name=request_file.filename,
                    file_bytes=await request_file.read(),
                )
                created_tokens.append(token)

        return created_tokens

    # NOTE if there is a directory in zip file, it fails
    async def save_file(self, file_name: str, file_bytes: bytes, token: uuid.UUID | None = None) -> uuid.UUID:
        if token is None:
            token = uuid.uuid4()

        _, extension = os.path.splitext(file_name)
        try:
            async with aiofiles.open(f"{self._DATA_DIR}/{token}{extension}", "wb") as file:
                await file.write(file_bytes)
            return token
        except FileNotFoundError:
            raise HTTPException(
                status_code=400, detail=f"Unable to save file {file_name}. Zip file maybe contains directories?"
            )
        except Exception as e:
            logger.error(f"Error while saving file {file_name}: {e}")
            raise HTTPException(status_code=400, detail=f"Unable to save file {file_name}.")

    async def fetch_file(self, file_name: str) -> bytes:
        try:
            async with aiofiles.open(f"{self._DATA_DIR}/{file_name}", "rb") as file:
                return await file.read()
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail=f"File {file_name} not found.")
        except Exception as e:
            logger.error(f"Error while fetching file {file_name}: {e}")
            raise HTTPException(status_code=400, detail=f"Unable to fetch file {file_name}.")
