from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, File, Query
from fastapi_utils.cbv import cbv

from api.enums import MoleculeFileExtensionEnum, MoleculeRepoSiteEnum
from api.schemas.fetched_file import FetchOnlineFileRequestDto, FetchOnlineFileResponseDto
from api.schemas.user_file import DownloadRequestDto, UploadRequestDto, UploadResponseDto
from containers import AppContainer
from services.data_fetcher_service import OnlineFileFetcherService
from services.file_storage_service import FileStorageService

io_router = APIRouter(tags=["I/O"])


@cbv(io_router)
class IORouter:
    @inject
    def __init__(
        self,
        storage_service: FileStorageService = Depends(Provide[AppContainer.file_storage_service]),
        fetcher_service: OnlineFileFetcherService = Depends(Provide[AppContainer.online_file_fetcher_service]),
    ):
        self.storage_service = storage_service
        self.fetcher_service = fetcher_service

    # @io_router.get("/download-files")
    # async def download_files(self, data: Annotated[DownloadRequestDto, Query()]):
    #     if len(file_names) == 1:
    #         pass
    #     files = await self.storage_service.download_files(data)
    #     return DownloadResponseDto(files=files)

    @io_router.post("/upload-files")
    async def upload_files(self, data: Annotated[UploadRequestDto, File()]) -> UploadResponseDto:
        files = [file async for file in self.storage_service.upload_files_from_request(data)]
        return UploadResponseDto(files=files)

    @io_router.get("/supported-site-extensions")
    async def get_supported_site_extensions(self, site: MoleculeRepoSiteEnum) -> list[MoleculeFileExtensionEnum]:
        supported_extensions = self.fetcher_service.get_supported_extensions(site)
        return supported_extensions

    @io_router.post("/fetch-online-file")
    async def fetch_online_file(self, data: FetchOnlineFileRequestDto) -> FetchOnlineFileResponseDto:
        cached, file_name = await self.fetcher_service.fetch_data(data)
        return FetchOnlineFileResponseDto(file=file_name, cached=cached)
