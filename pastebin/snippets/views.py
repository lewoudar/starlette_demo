import transaction
from sqlalchemy.orm import Session
from starlette.authentication import requires
from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse

from pastebin.utils import get_like_string
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
        snippet_schema = DefaultSnippetSchema(context={'request': request})
        snippets = request.state.db.query(Snippet).all()
        return JSONResponse(snippet_schema.dump(snippets, many=True))

    @requires(['authenticated', 'snippets:write'])
    async def post(self, request: Request) -> JSONResponse:
        db: Session = request.state.db
        snippet_schema = DefaultSnippetSchema(context={'request': request})
        payload = await request.json()
        snippet: Snippet = snippet_schema.load(payload)
        snippet.user = request.user
        db.add(snippet)
        db.flush()
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
        return JSONResponse(snippet_schema.dump(snippet))

    @requires(['authenticated', 'snippets:write'])
    def delete(self, request: Request) -> PlainTextResponse:
        snippet: Snippet = self.get_model_by_id(request, Snippet, request.path_params['id'])
        self.check_ownership(request, snippet.user)
        request.state.db.delete(snippet)
        transaction.commit()
        return PlainTextResponse('', status_code=204)
