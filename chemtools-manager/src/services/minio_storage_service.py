import uuid
import io
from minio import Minio
from minio.error import S3Error

from api.schemas.upload import UploadRequestDto
from conf.settings import MinIOSettings
from services import FileStorageService


class MinIOClient(FileStorageService):
    def __init__(self, minio_settings: MinIOSettings):
        self.client = Minio(
            endpoint=minio_settings.minio_endpoint,
            access_key=minio_settings.MINIO_ACCESS_KEY,
            secret_key=minio_settings.MINIO_SECRET_KEY,
            secure=minio_settings.MINIO_SECURE,
        )
        self.bucket_name = minio_settings.MINIO_BUCKET

        if not self.client.bucket_exists(self.bucket_name):
            self.client.make_bucket(self.bucket_name)

    async def upload_files(self, data: UploadRequestDto) -> list[uuid.UUID]:
        file_ids = []
        for file in data.files:
            file_id = await self.save_file(file.filename, await file.read())
            file_ids.append(file_id)
        return file_ids

    async def save_file(self, file_name: str, file_bytes: bytes, token: uuid.UUID | None = None) -> uuid.UUID:
        file_id = token or uuid.uuid4()
        object_name = f"{file_id}_{file_name}"

        try:
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                data=io.BytesIO(file_bytes),
                length=len(file_bytes),
                content_type="application/octet-stream",
            )
        except S3Error as e:
            raise RuntimeError(f"Failed to upload file: {e}")

        return file_id

    async def fetch_file(self, file_name: str) -> bytes:
        try:
            response = self.client.get_object(self.bucket_name, file_name)
            return response.read()
        except S3Error as e:
            raise RuntimeError(f"Failed to fetch file: {e}")
