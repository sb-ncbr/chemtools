from tortoise.models import Model
from tortoise import fields


class User(Model):
    id = fields.UUIDField(primary_key=True)
    email = fields.CharField(max_length=255)

    def __str__(self):
        return self.email
