from aio_pika import connect_robust
from minio import Minio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from conf.settings import MinIOSettings, PostgresSettings, RabbitMQSettings


class HealthcheckService:
    def __init__(
        self, postgres_settings: PostgresSettings, rabbitmq_settings: RabbitMQSettings, minio_settings: MinIOSettings
    ):
        self.postgres_settings = postgres_settings
        self.rabbitmq_settings = rabbitmq_settings
        self.minio_settings = minio_settings

    async def postgres_health(self):
        async_engine = create_async_engine(self.postgres_settings.postgres_url)
        try:
            async with async_engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
                return {"service": "PostgreSQL", "status": "UP"}
        except Exception as e:
            return {"service": "PostgreSQL", "status": "DOWN", "error": str(e)}
        finally:
            await async_engine.dispose()

    async def rabbitmq_health(self):
        try:
            conn = await connect_robust(self.rabbitmq_settings.rabbitmq_url)
            await conn.close()
            return {"service": "RabbitMQ", "status": "UP"}
        except Exception as e:
            return {"service": "RabbitMQ", "status": "DOWN", "error": str(e)}

    async def minio_health(self):
        try:
            client = Minio(
                endpoint=self.minio_settings.minio_endpoint,
                access_key=self.minio_settings.MINIO_ACCESS_KEY,
                secret_key=self.minio_settings.MINIO_SECRET_KEY,
                secure=self.minio_settings.MINIO_SECURE,
            )
            client.list_buckets()
            return {"service": "MinIO", "status": "UP"}
        except Exception as e:
            return {"service": "MinIO", "status": "DOWN", "error": str(e)}
