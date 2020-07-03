from marshmallow import Schema, fields, validate, post_dump, post_load
from starlette.requests import Request

from pastebin.mixins import SchemaMixin
from .models import LANGUAGES, STYLES, Snippet


class CommonSnippetSchema(SchemaMixin, Schema):
    linenos = fields.Boolean(required=False, default=False)

    @post_dump(pass_original=True)
    def add_user_url(self, data: dict, snippet: Snippet, **_) -> dict:
        request: Request = self.context['request']
        data['user'] = request.url_for('user_detail', id=snippet.user_id)
        return data


class DefaultSnippetSchema(CommonSnippetSchema):
    title = fields.String(required=True, validate=validate.Length(min=2, max=100))
    code = fields.String(required=True)
    language = fields.String(required=True, validate=validate.OneOf(LANGUAGES))
    style = fields.String(required=True, validate=validate.OneOf(STYLES))

    @post_load()
    def get_snippet(self, data: dict, **_) -> Snippet:
        return Snippet(**data)


class PatchSnippetSchema(CommonSnippetSchema):
    title = fields.String(validate=validate.Length(min=2, max=100))
    code = fields.String()
    language = fields.String(validate=validate.OneOf(LANGUAGES))
    style = fields.String(validate=validate.OneOf(STYLES))

    @post_load()
    def get_updated_snippet(self, data: dict, **_) -> Snippet:
        return self.get_updated_model(data)
