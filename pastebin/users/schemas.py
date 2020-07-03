from marshmallow import Schema, fields, validate, validates_schema, ValidationError, post_load

from pastebin.mixins import SchemaMixin
from .models import User


class DefaultUserSchema(SchemaMixin, Schema):
    first_name = fields.String(required=True, validate=validate.Length(min=2, max=100))
    last_name = fields.String(required=True, validate=validate.Length(min=2, max=100))
    pseudo = fields.String(required=True, validate=validate.Length(min=2, max=100))
    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True, validate=validate.Length(min=4, max=100))

    @post_load()
    def get_user(self, data: dict, **_) -> User:
        password = data.pop('password')
        user = User(**data)
        user.set_password(password)
        return user


# the difference here is that no field is required but there must be at least one field in the payload
class PatchUserSchema(SchemaMixin, Schema):
    first_name = fields.String(validate=validate.Length(min=2, max=100))
    last_name = fields.String(validate=validate.Length(min=2, max=100))
    pseudo = fields.String(validate=validate.Length(min=2, max=100))
    email = fields.Email()
    password = fields.String(load_only=True, validate=validate.Length(min=4, max=100))

    @validates_schema()
    def validate_non_empty_payload(self, data: dict, **_) -> None:
        if not data:
            raise ValidationError('payload must not be empty')

    @post_load()
    def get_updated_user(self, data: dict, **_) -> User:
        password = data.pop('password', None)
        user: User = self.get_updated_model(data)
        if password is not None:
            user.set_password(password)

        return user
