from typing import Callable

import transaction
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from zope.sqlalchemy import register


class DBSessionMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, database_url: str = 'sqlite:///:memory:'):
        super().__init__(app)
        self.database_url = database_url

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        engine = create_engine(self.database_url, connect_args={'check_same_thread': False})
        session_class = sessionmaker(bind=engine)
        db = session_class()
        register(db, transaction_manager=transaction.manager)
        request.state.db = db
        with transaction.manager:
            response = await call_next(request)
        db.close()
        return response
