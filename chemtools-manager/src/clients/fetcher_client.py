import logging
from typing import TYPE_CHECKING
import uuid

import httpx

from fastapi import HTTPException, status


if TYPE_CHECKING:
    from services import FileStorageService
    from api.models import FetchOnlineFileRequest


class OnlineFileFetcherClient:
    def __init__(self, storage_service: 'FileStorageService', logger: logging.Logger):
        self.__storage_service = storage_service
        self._logger = logger

    async def fetch_from(self, site_url: str, data: 'FetchOnlineFileRequest') -> uuid.UUID:
        data_bytes = await self._download(site_url.format(**data.model_dump()))
        token = uuid.uuid4()
        file_name = f"{data.molecule_id}.{data.extension}"
        await self.__storage_service.save_file(token, file_name, data_bytes)
        return token

    async def _download(self, full_url: str) -> dict:
        self._logger.info(f"Downloading file from url={full_url}")
        async with httpx.AsyncClient() as client:
            response = await client.get(full_url)
            if not response.is_success:
                if response.status_code == status.HTTP_404_NOT_FOUND:
                    self._logger.error(f"File cannot be fetched from url={full_url}")
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

                self._logger.error(f"Request failed with status code {response.status_code}")
                raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Service unavailable")

            return response.content
