import abc
import asyncio
import hashlib
import logging
import os
import uuid
from typing import AsyncGenerator

import aiofiles

from api.schemas.user_file import UploadRequestDto
from services.file_cache_service import FileCacheService
from utils import unzip_files

logger = logging.getLogger(__name__)


class FileStorageService(abc.ABC):
    def __init__(self, file_cache_service: FileCacheService):
        self.file_cache_service = file_cache_service

    @abc.abstractmethod
    async def push_file(self, file_name: str, file_bytes: bytes) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    async def fetch_file(self, file_name: str) -> bytes:
        raise NotImplementedError

    async def download_files(self, file_names: list[str], to_local_dir: str) -> list[str]:
        logger.debug(f"Downloading files={file_names} to {to_local_dir}")
        for idx, file_name_hash in enumerate(file_names):
            file_bytes, file_name = await asyncio.gather(
                self.fetch_file(file_name), self.file_cache_service.get_file_name(file_name_hash)
            )
            # NOTE be careful, this changes input_files
            file_names[idx] = file_name
            async with aiofiles.open(os.path.join(to_local_dir, file_name), "wb") as file:
                await file.write(file_bytes)

    async def upload_files(self, file_names: list[str], from_local_dir: str) -> None:
        logger.debug(f"Uploading files={file_names} from {from_local_dir}")
        for file_name in file_names:
            async with aiofiles.open(os.path.join(from_local_dir, file_name), "rb") as file:
                file_bytes = await file.read()
            await self.push_file(file_name, file_bytes)

    # NOTE there might be a filename collision when unzipping files from multiple zip files or
    # when uploading additional files with the same name
    async def upload_files_from_request(self, data: UploadRequestDto) -> AsyncGenerator[str, None]:
        for request_file in data.files:
            # NOTE if there is a directory in zip file, it fails
            if request_file.content_type == "application/zip":
                for file_name, file_func_wrapper in unzip_files(request_file.file).items():
                    yield await self.__process_file(file_name, file_func_wrapper(), data.user_id)
            else:
                yield await self.__process_file(request_file.filename, await request_file.read(), data.user_id)

    async def __process_file(self, file_name: str, file_content: str, user_id: uuid.UUID) -> str:
        file_name_hash = self.get_file_hash(file_content)
        await self.push_file(file_name=file_name_hash, file_bytes=file_content)
        await self.file_cache_service.create_user_file(user_id, file_name, file_name_hash)
        return file_name_hash

    @staticmethod
    def get_file_hash(file_bytes: bytes) -> str:
        hasher = hashlib.sha256()
        hasher.update(file_bytes)
        return hasher.hexdigest()
