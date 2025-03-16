import docker
from dependency_injector import containers, providers

import clients
import tools
from conf import settings
from db import repos
from db.database import DatabaseSessionManager
from services.calculation_service import CalculationService
from services.data_fetcher_service import OnlineFileFetcherService
from services.file_cache_service import FileCacheService
from services.message_broker_service import MessageBrokerService
from services.minio_storage_service import MinIOService
from services.pipeline_service import PipelineService
from services.worker_service import WorkerService


class AppContainer(containers.DeclarativeContainer):
    app_settings = providers.Singleton(settings.AppSettings)
    postgres_settings = providers.Singleton(settings.PostgresSettings)
    minio_settings = providers.Singleton(settings.MinIOSettings)
    rabbitmq_settings = providers.Singleton(settings.RabbitMQSettings)

    session_manager = providers.Singleton(DatabaseSessionManager)

    calculation_request_repo = providers.Singleton(
        repos.CalculationRequestRepo,
        session_manager=session_manager,
    )
    pipeline_repo = providers.Singleton(
        repos.PipelineRepo,
        session_manager=session_manager,
    )
    user_file_repo = providers.Singleton(
        repos.UserFileRepo,
        session_manager=session_manager,
    )
    fetched_file_repo = providers.Singleton(
        repos.FetchedFileRepo,
        session_manager=session_manager,
    )

    file_cache_service = providers.Singleton(
        FileCacheService, user_file_repo=user_file_repo, fetched_file_repo=fetched_file_repo
    )
    message_broker_service = providers.Singleton(
        MessageBrokerService,
        rabbitmq_settings=rabbitmq_settings,
    )
    calculation_service = providers.Singleton(
        CalculationService,
        calculation_request_repo=calculation_request_repo,
        message_broker_service=message_broker_service,
        file_cache_service=file_cache_service,
    )
    pipeline_service = providers.Singleton(
        PipelineService,
        pipeline_repo=pipeline_repo,
    )
    file_storage_service = providers.Singleton(
        MinIOService,
        file_cache_service=file_cache_service,
        minio_settings=minio_settings,
    )
    online_file_fetcher_client = providers.Singleton(
        clients.OnlineFileFetcherClient, storage_service=file_storage_service, file_cache_service=file_cache_service
    )
    online_file_fetcher_service = providers.Singleton(
        OnlineFileFetcherService, fetcher_client=online_file_fetcher_client
    )


class WorkerContainer(containers.DeclarativeContainer):
    worker_settings = providers.Singleton(settings.WorkerSettings)
    postgres_settings = providers.Singleton(settings.PostgresSettings)
    rabbitmq_settings = providers.Singleton(settings.RabbitMQSettings)

    docker = providers.Singleton(docker.from_env)

    session_manager = providers.Singleton(DatabaseSessionManager)

    calculation_request_repo = providers.Singleton(
        repos.CalculationRequestRepo,
        session_manager=session_manager,
    )
    calculation_result_repo = providers.Singleton(
        repos.CalculationResultRepo,
        session_manager=session_manager,
    )
    user_file_repo = providers.Singleton(
        repos.UserFileRepo,
        session_manager=session_manager,
    )
    fetched_file_repo = providers.Singleton(
        repos.FetchedFileRepo,
        session_manager=session_manager,
    )

    file_cache_service = providers.Singleton(
        FileCacheService, user_file_repo=user_file_repo, fetched_file_repo=fetched_file_repo
    )
    file_storage_service = providers.Singleton(
        MinIOService,
        minio_settings=AppContainer.minio_settings,
        file_cache_service=file_cache_service,
    )

    chargefw2_tool = providers.Singleton(tools.ChargeFW2Tool, file_storage_service=file_storage_service, docker=docker)
    mole2_tool = providers.Singleton(tools.Mole2Tool, file_storage_service=file_storage_service, docker=docker)
    gesamt_tool = providers.Singleton(tools.GesamtTool, file_storage_service=file_storage_service, docker=docker)

    worker_service = providers.Singleton(
        WorkerService,
        chargefw2_tool=chargefw2_tool,
        mole2_tool=mole2_tool,
        gesamt_tool=gesamt_tool,
        calculation_request_repo=calculation_request_repo,
        calculation_result_repo=calculation_result_repo,
    )
