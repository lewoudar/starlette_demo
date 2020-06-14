from datetime import datetime

import transaction
from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse
from starlette.authentication import requires

from pastebin.mixins import SAModelMixin
from pastebin.settings import DEFAULT_USER_GROUP
from .models import User, Group


class Users(HTTPEndpoint):

    @staticmethod
    def get(request: Request) -> JSONResponse:
        users = request.state.db.query(User).all()
        data = [
            {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'pseudo': user.pseudo,
                'created_at': str(user.created_at)
            } for user in users
        ]
        return JSONResponse(data)

    @staticmethod
    async def post(request: Request) -> JSONResponse:
        db = request.state.db
        payload = await request.json()
        password = payload.pop('password')
        user = User(**payload)
        user.set_password(password)
        group = db.query(Group).filter_by(name=DEFAULT_USER_GROUP).one()
        user.groups.append(group)
        db.add(user)
        db.flush()
        data = {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'pseudo': user.pseudo,
            'created_at': str(user.created_at)
        }
        return JSONResponse(data, status_code=201)


class UserInfo(SAModelMixin, HTTPEndpoint):

    def get(self, request: Request) -> JSONResponse:
        user = self.get_model_by_id(request, User, request.path_params['id'])

        return JSONResponse({
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'pseudo': user.pseudo,
            'created_at': str(user.created_at)
        })

    @requires(['authenticated', 'users:write'])
    async def put(self, request: Request) -> JSONResponse:
        user = self.get_model_by_id(request, User, request.path_params['id'])
        self.check_ownership(request, user)
        payload = await request.json()
        for item in ['created_at', 'updated_at', 'id']:
            payload.pop(item, None)
        password = payload.pop('password', None)
        if password is not None:
            user.set_password(password)

        for key, value in payload.items():
            setattr(user, key, value)
        user.updated_at = datetime.utcnow()

        request.state.db.flush()
        return JSONResponse({
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'pseudo': user.pseudo,
            'created_at': str(user.created_at)
        })

    @requires(['authenticated', 'users:write'])
    def delete(self, request: Request) -> PlainTextResponse:
        user = self.get_model_by_id(request, User, request.path_params['id'])
        self.check_ownership(request, user)
        request.state.db.delete(user)
        transaction.commit()
        return PlainTextResponse('', status_code=204)
