import abc
import uuid
from zipfile import ZipFile

from fastapi import File

from api.models import UploadRequest, UploadResponse


class FileStorageService(abc.ABC):
    def unzip_files(self, file: File):
        zip_file = ZipFile(file)
        # .read() surrounded in lambda to avoid storing all file contents in memory.
        # Also name=name is needed to avoid late binding.
        return {name: lambda name=name: zip_file.read(name) for name in zip_file.namelist()}

    @abc.abstractmethod
    async def upload_files(self, data: UploadRequest) -> UploadResponse:
        raise NotImplementedError

    @abc.abstractmethod
    async def fetch_files(self, token: uuid.UUID):
        raise NotImplementedError
