from sqlalchemy.orm import Session
from starlette.authentication import requires
from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse

from pastebin.utils import get_like_string
from .models import Language, Style, Snippet
from .schemas import DefaultSnippetSchema


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
