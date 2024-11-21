import logging

from dependency_injector import containers, providers
import httpx

import clients
import settings


class ApplicationContainer(containers.DeclarativeContainer):
    # remember to log (in a table) the following:
    # - charge params, other app params
    # - user ip
    # - auth/anonymous
    # - date and time
    logger = providers.Singleton(logging.getLogger, name="chemtools_api_logger")

    chemtools_manager_client = providers.Singleton(
        clients.ChemtoolsManagerClient,
        base_url=settings.CHEMTOOLS_MANAGER_CLIENT_URL,
        api_key="TODO",
        logger=logger,
        client=httpx.AsyncClient,
    )
