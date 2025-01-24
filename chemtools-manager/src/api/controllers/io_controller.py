from typing import Annotated

from dependency_injector.wiring import inject
from fastapi import APIRouter, File
from fastapi_utils.cbv import cbv

from api.enums import MoleculeFileExtensionEnum, MoleculeRepoSiteEnum
from api.schemas.online_fetch import FetchOnlineFileRequestDto, FetchOnlineFileResponseDto
from api.schemas.upload import UploadRequestDto, UploadResponseDto
from services import FileStorageService, OnlineFileFetcherService
from utils import from_app_container

io_router = APIRouter(tags=["I/O"])


@cbv(io_router)
class IOController:
    @inject
    def __init__(
        self,
        storage_service: FileStorageService = from_app_container("file_storage_service"),
        fetcher_service: OnlineFileFetcherService = from_app_container("online_file_fetcher_service"),
    ):
        self.__storage_service = storage_service
        self.__fetcher_service = fetcher_service

    @io_router.post("/custom_files/")
    async def upload_custom_files(self, data: Annotated[UploadRequestDto, File()]) -> UploadResponseDto:
        file_tokens = await self.__storage_service.upload_files(data)
        return UploadResponseDto(tokens=file_tokens)

    @io_router.get("/supported_site_extensions/")
    async def get_supported_site_extensions(self, site: MoleculeRepoSiteEnum) -> list[MoleculeFileExtensionEnum]:
        supported_extensions = self.__fetcher_service.get_supported_extensions(site)
        return supported_extensions

    @io_router.post("/fetch_online_file/")
    async def fetch_online_file(self, data: FetchOnlineFileRequestDto) -> FetchOnlineFileResponseDto:
        token = await self.__fetcher_service.fetch_data(data)
        return FetchOnlineFileResponseDto(token=token)
