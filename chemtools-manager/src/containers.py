import logging

from dependency_injector import containers, providers
import docker

import services
from tools import ChargeFW2Tool


class ApplicationContainer(containers.DeclarativeContainer):
    # config = providers.Configuration(yaml_files=["conf/di_config.yml"])
    logger = providers.Singleton(logging.getLogger, name="chemtools_manager_logger")

    docker = providers.Singleton(docker.from_env)

    storage_service = providers.Singleton(
        services.FileStorageService,
    )

    chargefw2_tool = providers.Singleton(ChargeFW2Tool, docker=docker, logger=logger)
