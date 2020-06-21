from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.routing import Mount

from .auth import BasicAuthBackend, on_auth_error
from .exceptions import http_exception, client_error, ClientError
from .middlewares import DBSessionMiddleware
from .settings import DATABASE_URL
from .users.urls import routes as user_routes

exception_handlers = {
    HTTPException: http_exception,
    ClientError: client_error
}

_middlewares = [
    Middleware(DBSessionMiddleware, database_url=DATABASE_URL),
    Middleware(AuthenticationMiddleware, backend=BasicAuthBackend(), on_error=on_auth_error)
]

app = Starlette(
    debug=True,
    routes=[
        Mount('/users', routes=user_routes)
    ],
    middleware=_middlewares,
    exception_handlers=exception_handlers
)
