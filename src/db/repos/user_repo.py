import uuid

from db.models import UserModel
from db.repos.base_repo import BaseRepo


class UserRepo(BaseRepo):
    _model = UserModel
