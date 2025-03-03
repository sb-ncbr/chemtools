from db.models.calculation import CalculationResultModel
from db.repos.base_repo import BaseRepo


class CalculationResultRepo(BaseRepo):
    _model = CalculationResultModel
