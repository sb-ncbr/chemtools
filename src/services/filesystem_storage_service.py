import logging
import os

import aiofiles

from conf.const import ROOT_DIR
from services.file_cache_service import FileCacheService
from services.file_storage_service import FileStorageService

logger = logging.getLogger(__name__)


class FilesystemStorageService(FileStorageService):
    _DATA_DIR = ROOT_DIR / "data/file_storage"

    def __init__(self, file_cache_service: FileCacheService):
        super().__init__(file_cache_service)
        if not os.path.exists(self._DATA_DIR):
            os.makedirs(self._DATA_DIR, exist_ok=True)

    async def push_file(self, file_name: str, file_bytes: bytes) -> str:
        try:
            async with aiofiles.open(self._DATA_DIR / file_name, "wb") as file:
                await file.write(file_bytes)
            return file_name
        except FileNotFoundError:
            raise RuntimeError(f"Unable to save file {file_name}. Zip file maybe contains directories?")
        except Exception as e:
            logger.error(f"Error while saving file {file_name}: {e}")
            raise RuntimeError(f"Unable to save file {file_name}.")

    async def fetch_file(self, file_name: str) -> bytes:
        try:
            async with aiofiles.open(self._DATA_DIR / file_name, "rb") as file:
                return await file.read()
        except FileNotFoundError:
            raise RuntimeError(f"File {file_name} not found.")
        except Exception as e:
            logger.error(f"Error while fetching file {file_name}: {e}")
            raise RuntimeError(f"Unable to fetch file {file_name}.")
