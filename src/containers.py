import docker
from dependency_injector import containers, providers

import clients
import services
import tools
from conf import settings
from db import repos
from db.database import DatabaseSessionManager


class AppContainer(containers.DeclarativeContainer):
    app_settings = providers.Singleton(settings.AppSettings)
    postgres_settings = providers.Singleton(settings.PostgresSettings)
    minio_settings = providers.Singleton(settings.MinIOSettings)
    rabbitmq_settings = providers.Singleton(settings.RabbitMQSettings)

    session_manager = providers.Singleton(DatabaseSessionManager)

    calculation_repo = providers.Singleton(
        repos.CalculationRepo,
        session_manager=session_manager,
    )
    user_repo = providers.Singleton(
        repos.UserRepo,
        session_manager=session_manager,
    )

    calculation_service = providers.Singleton(
        services.CalculationService,
        calculation_repo=calculation_repo,
    )
    user_service = providers.Singleton(
        services.UserService,
        user_repo=user_repo,
    )
    file_storage_service = providers.Singleton(
        services.MinIOService,
        minio_settings=minio_settings,
    )
    online_file_fetcher_client = providers.Singleton(
        clients.OnlineFileFetcherClient, storage_service=file_storage_service
    )
    online_file_fetcher_service = providers.Singleton(
        services.OnlineFileFetcherService, fetcher_client=online_file_fetcher_client
    )
    message_broker_service = providers.Singleton(
        services.MessageBrokerService,
        rabbitmq_settings=rabbitmq_settings,
    )


class WorkerContainer(containers.DeclarativeContainer):
    worker_settings = providers.Singleton(settings.WorkerSettings)
    postgres_settings = providers.Singleton(settings.PostgresSettings)
    rabbitmq_settings = providers.Singleton(settings.RabbitMQSettings)

    session_manager = providers.Singleton(DatabaseSessionManager)

    docker = providers.Singleton(docker.from_env)

    file_storage_service = providers.Singleton(
        services.MinIOService,
        minio_settings=AppContainer.minio_settings,
    )

    chargefw2_tool = providers.Singleton(tools.ChargeFW2Tool, file_storage_service=file_storage_service, docker=docker)
    mole2_tool = providers.Singleton(tools.Mole2Tool, file_storage_service=file_storage_service, docker=docker)
    gesamt_tool = providers.Singleton(tools.GesamtTool, file_storage_service=file_storage_service, docker=docker)
