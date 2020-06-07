from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse

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
                'pseudo': user.pseudo
            } for user in users
        ]
        return JSONResponse(data)

    @staticmethod
    async def post(request: Request):
        db = request.state.db
        payload = await request.json()
        user = User(**payload)
        db.add(user)
        db.flush()
        data = {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'pseudo': user.pseudo
        }
        return JSONResponse(data, status_code=201)


class UserInfo(HTTPEndpoint):
    def get(self, request: Request):
        pass

    async def put(self, request: Request):
        pass

    def delete(self, request: Request):
        pass
