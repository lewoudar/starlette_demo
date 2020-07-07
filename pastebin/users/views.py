import transaction
from sqlalchemy.orm import Session
from starlette.authentication import requires
from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse

from pastebin.mixins import SAModelMixin
from pastebin.settings import DEFAULT_USER_GROUP
from pastebin.utils import send_group, Operation, Model
from .models import User, Group
from .schemas import PatchUserSchema, DefaultUserSchema


class Users(HTTPEndpoint):
    user_schema = DefaultUserSchema()

    def get(self, request: Request) -> JSONResponse:
        users = request.state.db.query(User).all()
        return JSONResponse(self.user_schema.dump(users, many=True))

    async def post(self, request: Request) -> JSONResponse:
        db: Session = request.state.db
        payload = await request.json()
        user: User = self.user_schema.load(payload)
        group = db.query(Group).filter_by(name=DEFAULT_USER_GROUP).one()
        user.groups.append(group)
        db.add(user)
        db.flush()
        # websocket feed
        await send_group(Operation.CREATE, Model.USERS, {'id': user.id, 'pseudo': user.pseudo})
        return JSONResponse(self.user_schema.dump(user), status_code=201)


class UserInfo(SAModelMixin, HTTPEndpoint):
    user_schema = DefaultUserSchema()

    def get(self, request: Request) -> JSONResponse:
        user = self.get_model_by_id(request, User, request.path_params['id'])
        return JSONResponse(self.user_schema.dump(user))

    @requires(['authenticated', 'users:write'])
    async def patch(self, request: Request) -> JSONResponse:
        user = self.get_model_by_id(request, User, request.path_params['id'])
        self.check_ownership(request, user)
        payload = await request.json()
        user_schema = PatchUserSchema(context={'model': user})
        user: User = user_schema.load(payload)
        request.state.db.flush()
        # websocket feed
        await send_group(Operation.UPDATE, Model.USERS, {'id': user.id, 'pseudo': user.pseudo})
        return JSONResponse(user_schema.dump(user))

    @requires(['authenticated', 'users:write'])
    async def delete(self, request: Request) -> PlainTextResponse:
        user = self.get_model_by_id(request, User, request.path_params['id'])
        self.check_ownership(request, user)
        # websocket feed
        await send_group(Operation.DELETE, Model.USERS, {'id': user.id, 'pseudo': user.pseudo})
        request.state.db.delete(user)
        transaction.commit()
        return PlainTextResponse('', status_code=204)
