import logging

import docker
from dependency_injector import containers, providers

import clients
import services
import tools


class ApplicationContainer(containers.DeclarativeContainer):
    # config = providers.Configuration(yaml_files=["conf/di_config.yml"])
    docker = providers.Singleton(docker.from_env)

    file_storage_service = providers.Singleton(services.FilesystemStorageService)

    online_file_fetcher_client = providers.Singleton(
        clients.OnlineFileFetcherClient, storage_service=file_storage_service
    )

    online_file_fetcher_service = providers.Singleton(
        services.OnlineFileFetcherService, fetcher_client=online_file_fetcher_client
    )

    chargefw2_tool = providers.Singleton(tools.ChargeFW2Tool, file_storage_service=file_storage_service, docker=docker)
    mole2_tool = providers.Singleton(tools.Mole2Tool, file_storage_service=file_storage_service, docker=docker)
    gesamt_tool = providers.Singleton(tools.GesamtTool, file_storage_service=file_storage_service, docker=docker)
