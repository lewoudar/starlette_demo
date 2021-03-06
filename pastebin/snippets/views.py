import transaction
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from sqlalchemy.orm import Session
from starlette.authentication import requires
from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse, Response

from pastebin.utils import get_like_string, send_group, Operation, Model, Paginator
from .models import Language, Style, Snippet
from .schemas import DefaultSnippetSchema, PatchSnippetSchema
from ..mixins import SAModelMixin


def get_languages(request: Request) -> JSONResponse:
    db: Session = request.state.db
    name = request.query_params.get('name')
    if name is not None:
        languages = db.query(Language).filter(Language.name.ilike(get_like_string(name))).all()
    else:
        languages = db.query(Language).all()
    return JSONResponse([language.name for language in languages])


def get_styles(request: Request) -> JSONResponse:
    db: Session = request.state.db
    name = request.query_params.get('name')
    if name is not None:
        styles = db.query(Style).filter(Style.name.ilike(get_like_string(name))).all()
    else:
        styles = request.state.db.query(Style).all()
    return JSONResponse([style.name for style in styles])


class Snippets(HTTPEndpoint):

    @staticmethod
    def get(request: Request) -> JSONResponse:
        paginator = Paginator(request, Snippet, DefaultSnippetSchema(context={'request': request}))
        return JSONResponse(paginator.render())

    @requires(['authenticated', 'snippets:write'])
    async def post(self, request: Request) -> JSONResponse:
        db: Session = request.state.db
        snippet_schema = DefaultSnippetSchema(context={'request': request})
        payload = await request.json()
        snippet: Snippet = snippet_schema.load(payload)
        snippet.user = request.user
        db.add(snippet)
        db.flush()
        # websocket feed
        await send_group(Operation.CREATE, Model.SNIPPETS, {
            'id': snippet.id,
            'title': snippet.title,
            'owner': snippet.user.pseudo
        })
        return JSONResponse(snippet_schema.dump(snippet))


class SnippetInfo(SAModelMixin, HTTPEndpoint):

    def get(self, request: Request) -> JSONResponse:
        snippet_schema = DefaultSnippetSchema(context={'request': request})
        snippet = self.get_model_by_id(request, Snippet, request.path_params['id'])
        return JSONResponse(snippet_schema.dump(snippet))

    @requires(['authenticated', 'snippets:write'])
    async def patch(self, request: Request) -> JSONResponse:
        snippet: Snippet = self.get_model_by_id(request, Snippet, request.path_params['id'])
        snippet_schema = PatchSnippetSchema(context={'request': request, 'model': snippet})
        self.check_ownership(request, snippet.user)

        payload = await request.json()
        snippet: Snippet = snippet_schema.load(payload)
        request.state.db.flush()
        # websocket feed
        await send_group(Operation.UPDATE, Model.SNIPPETS, {
            'id': snippet.id,
            'title': snippet.title,
            'owner': snippet.user.pseudo
        })
        return JSONResponse(snippet_schema.dump(snippet))

    @requires(['authenticated', 'snippets:write'])
    async def delete(self, request: Request) -> PlainTextResponse:
        snippet: Snippet = self.get_model_by_id(request, Snippet, request.path_params['id'])
        self.check_ownership(request, snippet.user)
        # websocket feed
        await send_group(Operation.DELETE, Model.SNIPPETS, {
            'id': snippet.id,
            'title': snippet.title,
            'owner': snippet.user.pseudo
        })
        request.state.db.delete(snippet)
        transaction.commit()
        return PlainTextResponse('', status_code=204)


class SnippetHighlight(SAModelMixin, HTTPEndpoint):

    def get(self, request: Request) -> Response:
        snippet = self.get_model_by_id(request, Snippet, request.path_params['id'])
        lexer = get_lexer_by_name(snippet.language)
        formatter = HtmlFormatter(title=snippet.title, style=snippet.style, linenos=snippet.linenos)
        context = {
            'request': request,
            'title': snippet.title,
            'highlighted': highlight(snippet.code, lexer, formatter)
        }
        return request.app.state.templates.TemplateResponse('highlight.jinja2', context)
