import docker
from dependency_injector import containers, providers

import clients
from conf import settings
import services
import tools


class AppContainer(containers.DeclarativeContainer):
    app_settings = providers.Singleton(settings.AppSettings)
    minio_settings = providers.Singleton(settings.MinIOSettings)
    rabbitmq_settings = providers.Singleton(settings.RabbitMQSettings)

    file_storage_service = providers.Singleton(
        services.MinIOClient,
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
    rabbitmq_settings = providers.Singleton(settings.RabbitMQSettings)

    docker = providers.Singleton(docker.from_env)

    file_storage_service = providers.Singleton(
        services.MinIOClient,
        minio_settings=AppContainer.minio_settings,
    )

    chargefw2_tool = providers.Singleton(tools.ChargeFW2Tool, file_storage_service=file_storage_service, docker=docker)
    mole2_tool = providers.Singleton(tools.Mole2Tool, file_storage_service=file_storage_service, docker=docker)
    gesamt_tool = providers.Singleton(tools.GesamtTool, file_storage_service=file_storage_service, docker=docker)
