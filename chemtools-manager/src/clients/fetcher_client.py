import logging
import uuid
from typing import TYPE_CHECKING

import httpx
from fastapi import HTTPException, status

if TYPE_CHECKING:
    from api.schemas.online_fetch import FetchOnlineFileRequestDto
    from services import FileStorageService

logger = logging.getLogger(__name__)


class OnlineFileFetcherClient:
    def __init__(self, storage_service: 'FileStorageService'):
        self.__storage_service = storage_service

    async def fetch_from(self, site_url: str, data: 'FetchOnlineFileRequestDto') -> str:
        data_bytes = await self._download(site_url.format(**data.model_dump()))
        file_name = f"{data.molecule_id}.{data.extension}"
        remote_file = await self.__storage_service.push_file(file_name, data_bytes)
        return remote_file

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
