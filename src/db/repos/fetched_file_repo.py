import uuid
from sqlalchemy import select

from db.models.fetched_file import FetchedFileModel
from db.repos.base_repo import BaseRepo


class FetchedFileRepo(BaseRepo):
    _model = FetchedFileModel

    async def get_matching_files(self, file_names: list[str]) -> list[FetchedFileModel]:
        async with self.session_manager.session() as db:
            return (
                (await db.execute(select(self._model).filter(self._model.file_name_hash.in_(file_names))))
                .scalars()
                .all()
            )
