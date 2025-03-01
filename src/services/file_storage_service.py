import abc
import logging
import os
import uuid

import aiofiles

from api.schemas.upload import UploadRequestDto
from utils import unzip_files

logger = logging.getLogger(__name__)


class FileStorageService(abc.ABC):
    @abc.abstractmethod
    async def push_file(self, file_name: str, file_bytes: bytes) -> uuid.UUID:
        raise NotImplementedError

    @abc.abstractmethod
    async def fetch_file(self, file_name: str) -> bytes:
        raise NotImplementedError

    async def download_files(self, file_names: list[str], to_local_dir: str) -> None:
        logger.debug(f"Downloading files={file_names} to {to_local_dir}")
        for file_name in file_names:
            file_bytes = await self.fetch_file(file_name)
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
    async def upload_files_from_request(self, data: UploadRequestDto) -> list[uuid.UUID]:
        created_tokens = []
        for request_file in data.files:
            if request_file.content_type == "application/zip":
                for file_name, file_func_wrapper in unzip_files(request_file.file).items():
                    remote_name = await self.push_file(file_name=file_name, file_bytes=file_func_wrapper())
                    created_tokens.append(remote_name)

            else:
                remote_name = await self.push_file(
                    file_name=request_file.filename,
                    file_bytes=await request_file.read(),
                )
                created_tokens.append(remote_name)

        return created_tokens
