from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.routing import Mount

from .middlewares import DBSessionMiddleware
from .settings import TESTING, DATABASE_URL, TEST_DATABASE_URL
from .users.urls import routes as user_routes

database_url = TEST_DATABASE_URL if TESTING else DATABASE_URL
app = Starlette(
    debug=True,
    routes=[
        Mount('/users', routes=user_routes)
    ],
    middleware=[Middleware(DBSessionMiddleware, database_url=database_url)]
)
