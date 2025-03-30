import uuid

from api.schemas.fetched_file import FetchedFileDto, FetchOnlineFileRequestDto
from db.models.fetched_file import FetchedFileModel
from db.models.user_file import UserFileModel
from db.repos.fetched_file_repo import FetchedFileRepo
from db.repos.user_file_repo import UserFileRepo


class FileCacheService:
    def __init__(self, user_file_repo: UserFileRepo, fetched_file_repo: FetchedFileRepo):
        self.user_file_repo = user_file_repo
        self.fetched_file_repo = fetched_file_repo

    async def get_fetched_file(self, file_data: FetchOnlineFileRequestDto) -> FetchedFileDto | None:
        fetched_file = await self.fetched_file_repo.get_by(
            molecule_id=file_data.molecule_id, site=file_data.site, extension=file_data.extension
        )
        return fetched_file and FetchedFileDto.model_validate(fetched_file)

    async def create_fetched_file(
        self, file_data: FetchOnlineFileRequestDto, file_name: str, file_name_hash: str
    ) -> FetchedFileModel:
        return await self.fetched_file_repo.create(
            FetchedFileModel(**file_data.model_dump(), file_name=file_name, file_name_hash=file_name_hash)
        )

    async def create_user_file(self, user_id: uuid.UUID | None, file_name: str, file_name_hash: str) -> UserFileModel:
        if user_file := await self.user_file_repo.get_by(user_id=user_id, file_name_hash=file_name_hash):
            return user_file
        return await self.user_file_repo.create(
            UserFileModel(user_id=user_id, file_name=file_name, file_name_hash=file_name_hash)
        )

    async def do_files_exist(self, file_names: list[str]) -> bool:
        user_files = await self.user_file_repo.get_matching_files(file_names)
        fetched_files = await self.fetched_file_repo.get_matching_files(file_names)
        return len(set(file_obj.file_name_hash for file_obj in user_files + fetched_files)) == len(file_names)

    async def get_file_name(self, file_name_hash: str) -> str:
        if user_file := await self.user_file_repo.get_by(file_name_hash=file_name_hash):
            return user_file.file_name
        fetched_file = await self.fetched_file_repo.get_by(file_name_hash=file_name_hash)
        return fetched_file.file_name

    async def get_files_by(self, user_id: uuid.UUID, file_names: list[str]) -> list[FetchedFileModel | UserFileModel]:
        user_files = await self.user_file_repo.get_user_matching_files(user_id, file_names)
        fetched_files = await self.fetched_file_repo.get_matching_files(file_names)
        return [*user_files, *fetched_files]
