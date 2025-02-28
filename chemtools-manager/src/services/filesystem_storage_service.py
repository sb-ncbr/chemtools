import logging
import os
import uuid

import aiofiles
from fastapi import HTTPException

from services import FileStorageService

logger = logging.getLogger(__name__)


class FilesystemStorageService(FileStorageService):
    _DATA_DIR = "../data/file_storage"

    def __init__(self, *args, **kwargs):
        if not os.path.exists(self._DATA_DIR):
            os.makedirs(self._DATA_DIR)
        super().__init__(*args, **kwargs)

    # NOTE if there is a directory in zip file, it fails
    async def push_file(self, file_name: str, file_bytes: bytes, token: uuid.UUID | None = None) -> uuid.UUID:
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
