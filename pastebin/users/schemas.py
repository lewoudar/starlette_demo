from datetime import datetime

from marshmallow import Schema, fields, validate, validates_schema, ValidationError, post_load

from pastebin.mixins import ErrorSchemaMixin
from .models import User


class DefaultUserSchema(ErrorSchemaMixin, Schema):
    id = fields.Integer(required=True, dump_only=True)
    first_name = fields.String(required=True, validate=validate.Length(min=2, max=100))
    last_name = fields.String(required=True, validate=validate.Length(min=2, max=100))
    pseudo = fields.String(required=True, validate=validate.Length(min=2, max=100))
    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True, validate=validate.Length(min=4, max=100))
    created_at = fields.DateTime(required=True, dump_only=True)

    @post_load()
    def get_user(self, data: dict, **_) -> User:
        password = data.pop('password')
        user = User(**data)
        user.set_password(password)
        return user


# the difference here is that no field is required but there must be at least one field in the payload
class PatchUserSchema(ErrorSchemaMixin, Schema):
    id = fields.Integer(dump_only=True)
    first_name = fields.String(validate=validate.Length(min=2, max=100))
    last_name = fields.String(validate=validate.Length(min=2, max=100))
    pseudo = fields.String(validate=validate.Length(min=2, max=100))
    email = fields.Email()
    password = fields.String(load_only=True, validate=validate.Length(min=4, max=100))
    created_at = fields.DateTime(dump_only=True)

    @validates_schema()
    def validate_non_empty_payload(self, data: dict, **_) -> None:
        if not data:
            raise ValidationError('payload must not be empty')

    @post_load()
    def get_updated_user(self, data: dict, **_) -> User:
        user: User = self.context['user']
        password = data.pop('password', None)

        if password is not None:
            user.set_password(password)
        for key, value in data.items():
            setattr(user, key, value)

        user.updated_at = datetime.utcnow()
        return user
