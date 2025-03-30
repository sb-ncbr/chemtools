import abc
import hashlib
import io
import logging
import os
import uuid
import zipfile
from datetime import datetime
from typing import AsyncGenerator

import aiofiles

from api.schemas.user_file import DownloadRequestDto, UploadRequestDto, UserFileDto
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
        for file_name in file_names:
            file_bytes = await self.fetch_file(file_name)
            async with aiofiles.open(os.path.join(to_local_dir, file_name), "wb") as file:
                await file.write(file_bytes)

    async def upload_files(self, file_names: list[str], from_local_dir: str) -> AsyncGenerator[UserFileDto, None]:
        logger.debug(f"Uploading files={file_names} from {from_local_dir}")
        for file_name in file_names:
            async with aiofiles.open(os.path.join(from_local_dir, file_name), "rb") as file:
                file_bytes = await file.read()
            yield await self.__process_file(file_name, file_bytes)

    async def download_files_from_request(self, data: DownloadRequestDto):
        logger.debug(f"Downloading files={data.file_names}")

        file_dtos = await self.file_cache_service.get_files_by(data.user_id, data.file_names)
        if len(file_dtos) != len(data.file_names):
            raise FileNotFoundError(
                f"Files not found: {set(data.file_names) - {file_dto.file_name for file_dto in file_dtos}}"
            )

        file_buffer = io.BytesIO()
        if len(file_dtos) == 1:
            file_bytes = await self.fetch_file(file_dtos[0].file_name_hash)
            file_buffer.write(file_bytes)
        else:
            with zipfile.ZipFile(file_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for file_dto in file_dtos:
                    file_bytes = await self.fetch_file(file_dto.file_name_hash)
                    zip_file.writestr(file_dto.file_name, file_bytes.decode("utf-8"))
        file_buffer.seek(0)

        time_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_name = file_dtos[0].file_name if len(file_dtos) == 1 else f"files_bundle_{time_str}.zip"
        return file_buffer, file_name

    # NOTE there might be a filename collision when unzipping files from multiple zip files or
    # when uploading additional files with the same name
    async def upload_files_from_request(self, data: UploadRequestDto) -> AsyncGenerator[str, None]:
        for request_file in data.files:
            # NOTE if there is a directory in zip file, it fails
            if request_file.content_type == "application/zip":
                for file_name, file_func_wrapper in unzip_files(request_file.file).items():
                    user_file_dto = await self.__process_file(file_name, file_func_wrapper(), data.user_id)
                    yield user_file_dto.file_name_hash
            else:
                user_file_dto = await self.__process_file(
                    request_file.filename, await request_file.read(), data.user_id
                )
                yield user_file_dto.file_name_hash

    async def __process_file(self, file_name: str, file_content: str, user_id: uuid.UUID | None = None) -> UserFileDto:
        file_name_hash = self.get_file_hash(file_content)
        file_extension = os.path.splitext(file_name)[1]
        new_file_name = f"{file_name_hash}{file_extension}"

        await self.push_file(file_name=new_file_name, file_bytes=file_content)
        user_file = await self.file_cache_service.create_user_file(user_id, file_name, new_file_name)
        return UserFileDto.model_validate(user_file)

    @staticmethod
    def get_file_hash(file_bytes: bytes) -> str:
        hasher = hashlib.sha256()
        hasher.update(file_bytes)
        return hasher.hexdigest()
