import abc
import logging
from typing import Callable
import uuid
from zipfile import ZipFile

from fastapi import File

from api.models import UploadRequest


class FileStorageService(abc.ABC):
    def __init__(self, logger: logging.Logger):
        self._logger = logger

    def unzip_files(self, file: File) -> dict[str, Callable[[str], bytes]]:
        zip_file = ZipFile(file)
        # .read() surrounded in lambda to avoid storing all file contents in memory.
        # Also name=name is needed to avoid late binding.
        return {name: lambda name=name: zip_file.read(name) for name in zip_file.namelist()}

    @abc.abstractmethod
    async def upload_files(self, data: UploadRequest) -> uuid.UUID:
        raise NotImplementedError

    @abc.abstractmethod
    async def save_file(self, token: uuid.UUID, file_name: str, file_bytes: bytes) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def fetch_files(self, token: uuid.UUID):
        raise NotImplementedError
