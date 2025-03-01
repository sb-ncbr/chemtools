
from db.models.calculation import CalculationModel
from db.repos.base_repo import BaseRepo


class CalculationRepo(BaseRepo):
    _model = CalculationModel
