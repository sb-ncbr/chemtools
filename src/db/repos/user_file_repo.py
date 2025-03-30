import uuid
from sqlalchemy import select

from db.models.user_file import UserFileModel
from db.repos.base_repo import BaseRepo


class UserFileRepo(BaseRepo):
    _model = UserFileModel

    async def get_matching_files(self, file_names: list[str]) -> list[UserFileModel]:
        async with self.session_manager.session() as db:
            return (
                (await db.execute(select(self._model).filter(self._model.file_name_hash.in_(file_names))))
                .scalars()
                .all()
            )

    async def get_user_matching_files(self, user_id: uuid.UUID, file_names: list[str]) -> list[UserFileModel]:
        async with self.session_manager.session() as db:
            return (
                (
                    await db.execute(
                        select(self._model)
                        .filter(self._model.user_id == user_id)
                        .filter(self._model.file_name_hash.in_(file_names))
                    )
                )
                .scalars()
                .all()
            )
