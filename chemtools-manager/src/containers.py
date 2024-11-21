import logging

from dependency_injector import containers, providers
import docker

import services
import tools


class ApplicationContainer(containers.DeclarativeContainer):
    # config = providers.Configuration(yaml_files=["conf/di_config.yml"])
    logger = providers.Singleton(logging.getLogger, name="chemtools_manager_logger")

    docker = providers.Singleton(docker.from_env)

    storage_service = providers.Singleton(
        services.FilesystemStorageService,
    )

    chargefw2_tool = providers.Singleton(tools.ChargeFW2Tool, docker=docker, logger=logger)
