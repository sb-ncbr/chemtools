import io

from minio import Minio
from minio.error import S3Error

from conf.settings import MinIOSettings
from services.file_cache_service import FileCacheService
from services.file_storage_service import FileStorageService


class MinIOService(FileStorageService):
    def __init__(self, minio_settings: MinIOSettings, file_cache_service: FileCacheService):
        super().__init__(file_cache_service)
        self.client = Minio(
            endpoint=minio_settings.minio_endpoint,
            access_key=minio_settings.MINIO_ACCESS_KEY,
            secret_key=minio_settings.MINIO_SECRET_KEY,
            secure=minio_settings.MINIO_SECURE,
        )
        self.bucket_name = minio_settings.MINIO_BUCKET

        if not self.client.bucket_exists(self.bucket_name):
            self.client.make_bucket(self.bucket_name)

    async def push_file(self, file_name: str, file_bytes: bytes) -> str:
        try:
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=file_name,
                data=io.BytesIO(file_bytes),
                length=len(file_bytes),
                content_type="application/octet-stream",
            )
        except S3Error as e:
            raise RuntimeError(f"Failed to upload file: {e}")

        return file_name

    async def fetch_file(self, file_name: str) -> bytes:
        try:
            response = self.client.get_object(self.bucket_name, file_name)
            return response.read()
        except S3Error as e:
            raise RuntimeError(f"Failed to fetch file: {e}")
