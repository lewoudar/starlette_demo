from datetime import datetime

from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse

from pastebin.mixins import SAModelMixin
from .models import User


class Users(HTTPEndpoint):

    @staticmethod
    def get(request: Request):
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
    async def post(request: Request):
        db = request.state.db
        payload = await request.json()
        password = payload.pop('password')
        user = User(**payload)
        user.set_password(password)
        db.add(user)
        db.flush()
        data = {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'pseudo': user.pseudo,
            'created_at': user.created_at
        }
        return JSONResponse(data, status_code=201)


class UserInfo(SAModelMixin, HTTPEndpoint):

    def get(self, request: Request):
        user = self.get_model_by_id(request, User, request.path_params['id'])

        return JSONResponse({
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'pseudo': user.pseudo,
            'created_at': str(user.created_at)
        })

    async def put(self, request: Request):
        user = self.get_model_by_id(request, User, request.path_params['id'])
        payload = await request.json()
        for item in ['created_at', 'updated_at', 'id', 'password']:
            payload.pop(item, None)

        for key, value in payload.items():
            setattr(user, key, value)
        user.updated_at = datetime.now()

        request.state.db.flush()
        return JSONResponse({
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'pseudo': user.pseudo,
            'created_at': str(user.created_at)
        })

    def delete(self, request: Request):
        pass
