import uuid
from sqlalchemy import select
from db.models import PipelineItemModel
from db.repos.base_repo import BaseRepo

from sqlalchemy.orm import selectinload


class PipelineItemRepo(BaseRepo):
    _model = PipelineItemModel
