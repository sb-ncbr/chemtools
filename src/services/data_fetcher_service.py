from fastapi import HTTPException

from api.enums import MoleculeFileExtensionEnum, MoleculeRepoSiteEnum
from api.schemas.fetched_file import FetchOnlineFileRequestDto
from clients import OnlineFileFetcherClient


class DataFetcherService:
    def __init__(self, fetcher_client: OnlineFileFetcherClient):
        self.fetcher_client = fetcher_client

    async def fetch_data(self, data: FetchOnlineFileRequestDto) -> tuple[bool, str]:
        if not (site_url := data.site.get_site_url()):
            raise NotImplementedError(f'Missing url mapping for "{data.site}" site')

        if data.extension not in self.get_supported_extensions(data.site):
            raise HTTPException(status_code=400, detail=f'"{data.extension}" is not supported for "{data.site}"')

        return await self.fetcher_client.fetch_from(site_url, data)

    def get_supported_extensions(self, site: MoleculeRepoSiteEnum) -> list[MoleculeFileExtensionEnum]:
        if not (site_extensions := site.get_site_extensions()):
            raise NotImplementedError(f'Missing extension mapping for "{site}" site')

        return site_extensions
