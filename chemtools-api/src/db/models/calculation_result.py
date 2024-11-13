from tortoise.models import Model
from tortoise import fields

from db.enums import CalculationToolType


class CalculationResult(Model):
    id = fields.UUIDField(primary_key=True)
    type = fields.CharEnumField(enum_type=CalculationToolType)

    def __str__(self):
        return self.type
