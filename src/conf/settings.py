import os
from pydantic_settings import BaseSettings, SettingsConfigDict

from conf.const import ROOT_DIR


class BaseEnvSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT_DIR / ".env", extra="ignore")


class AppSettings(BaseEnvSettings):
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    LOG_LEVEL: str = "INFO"
    PIPELINE_ACCEPTED_HOSTS: str = "0.0.0.0"


class WorkerSettings(BaseEnvSettings):
    LOG_LEVEL: str = "INFO"


class PostgresSettings(BaseEnvSettings):
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "chemtools-db"

    @property
    def postgres_url(self):
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


class RabbitMQSettings(BaseEnvSettings):
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASSWORD: str = "guest"
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672

    @property
    def rabbitmq_url(self):
        return f"pyamqp://{self.RABBITMQ_USER}:{self.RABBITMQ_PASSWORD}@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}//"


class MinIOSettings(BaseEnvSettings):
    MINIO_HOST: str = "localhost"
    MINIO_PORT: int = 9000
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_BUCKET: str = "file-storage"
    MINIO_SECURE: bool = False

    @property
    def minio_endpoint(self):
        return f"{self.MINIO_HOST}:{self.MINIO_PORT}"
