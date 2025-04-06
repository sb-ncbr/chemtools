import logging

import httpx
from fastapi import HTTPException, status

from api.schemas.fetched_file import FetchOnlineFileRequestDto
from services.file_cache_service import FileCacheService
from services.file_storage_service import FileStorageService

logger = logging.getLogger(__name__)


class OnlineFileFetcherClient:
    def __init__(self, storage_service: FileStorageService, file_cache_service: FileCacheService):
        self.storage_service = storage_service
        self.file_cache_service = file_cache_service

    async def fetch_from(self, site_url: str, data: FetchOnlineFileRequestDto) -> tuple[bool, str]:
        # Try obtaining the file hash from db (if the file was fetched before)
        fetched_file = await self.file_cache_service.get_fetched_file(data)
        data_dict = data.model_dump()
        if not data_dict.pop("force_download") and fetched_file:
            return True, fetched_file.file_name_hash

        # Otherwise fetch the file and save to db as cache
        data_bytes = await self._download(site_url.format(**data_dict))
        file_name = f"{data.molecule_id}.{data.extension}"
        file_name_hash = f"{self.storage_service.get_file_hash(data_bytes)}.{data.extension}"
        await self.storage_service.push_file(file_name_hash, data_bytes)
        await self.file_cache_service.create_fetched_file(data, file_name, file_name_hash)
        return False, file_name_hash

    async def _download(self, full_url: str) -> dict:
        logger.info(f"Downloading file from url={full_url}")
        async with httpx.AsyncClient() as client:
            response = await client.get(full_url)
            if not response.is_success:
                if response.status_code == status.HTTP_404_NOT_FOUND:
                    logger.error(f"File cannot be fetched from url={full_url}")
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

                logger.error(f"Request failed with status code {response.status_code}")
                raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Service unavailable")

            return response.content
