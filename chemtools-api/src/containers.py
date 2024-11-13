import logging

from dependency_injector import containers, providers

import clients
import settings


class ApplicationContainer(containers.DeclarativeContainer):
    logger = providers.Singleton(logging.getLogger, name="chemtools_api_logger")

    chemtools_manager_client = providers.Singleton(
        clients.ChemtoolsManagerClient, base_url=settings.CHEMTOOLS_MANAGER_CLIENT_URL, api_key="TODO", logger=logger
    )
