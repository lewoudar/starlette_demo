from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.middleware import Middleware
from starlette.routing import Mount

from .middlewares import DBSessionMiddleware
from .settings import TESTING, DATABASE_URL, TEST_DATABASE_URL
from .exceptions import http_exception
from .users.urls import routes as user_routes

database_url = TEST_DATABASE_URL if TESTING else DATABASE_URL

exception_handlers = {
    HTTPException: http_exception
}

app = Starlette(
    debug=True,
    routes=[
        Mount('/users', routes=user_routes)
    ],
    middleware=[Middleware(DBSessionMiddleware, database_url=database_url)],
    exception_handlers=exception_handlers
)
