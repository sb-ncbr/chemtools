import uuid
from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, File, HTTPException, Query
from fastapi.responses import StreamingResponse
from fastapi_utils.cbv import cbv

from api.enums import MoleculeFileExtensionEnum, MoleculeRepoSiteEnum
from api.schemas.fetched_file import FetchOnlineFileRequestDto, FetchOnlineFileResponseDto
from api.schemas.user_file import DownloadRequestDto, UploadRequestDto, UploadResponseDto, UserFileDto
from containers import AppContainer
from services.data_fetcher_service import DataFetcherService
from services.file_cache_service import FileCacheService
from services.file_storage_service import FileStorageService

io_router = APIRouter(tags=["I/O"])


@cbv(io_router)
class IORouter:
    @inject
    def __init__(
        self,
        storage_service: FileStorageService = Depends(Provide[AppContainer.file_storage_service]),
        fetcher_service: DataFetcherService = Depends(Provide[AppContainer.data_fetcher_service]),
        file_cache_service: FileCacheService = Depends(Provide[AppContainer.file_cache_service]),
    ):
        self.storage_service = storage_service
        self.fetcher_service = fetcher_service
        self.file_cache_service = file_cache_service

    @io_router.get("/files")
    async def download_files(self, data: Annotated[DownloadRequestDto, Query()]) -> StreamingResponse:
        try:
            file_buffer, file_name = await self.storage_service.download_files_from_request(data)
        except FileNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))

        return StreamingResponse(
            file_buffer,
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename={file_name}"},
        )

    @io_router.post("/files")
    async def upload_files(self, data: Annotated[UploadRequestDto, File()]) -> UploadResponseDto:
        files = [file async for file in self.storage_service.upload_files_from_request(data)]
        return UploadResponseDto(files=files)

    @io_router.get("/supported-site-extensions")
    async def get_supported_site_extensions(self, site: MoleculeRepoSiteEnum) -> list[MoleculeFileExtensionEnum]:
        supported_extensions = self.fetcher_service.get_supported_extensions(site)
        return supported_extensions

    @io_router.get("/online-file")
    async def fetch_online_file(
        self, data: Annotated[FetchOnlineFileRequestDto, Query()]
    ) -> FetchOnlineFileResponseDto:
        cached, file_name = await self.fetcher_service.fetch_data(data)
        return FetchOnlineFileResponseDto(file=file_name, cached=cached)

    @io_router.get("/user/files")
    async def get_user_files(self, user_id: uuid.UUID) -> list[UserFileDto]:
        files = await self.file_cache_service.get_user_files(user_id)
        return [UserFileDto.model_validate(file) for file in files]
