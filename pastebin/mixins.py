from marshmallow import ValidationError
from starlette.exceptions import HTTPException
from starlette.requests import Request

from pastebin.users.models import User, Base as Model
from .exceptions import BadRequestError


class SAModelMixin:

    @staticmethod
    def get_model_by_id(request: Request, model: Model, model_id: int) -> Model:
        sa_model = request.state.db.query(model).filter(model.id == model_id).one_or_none()
        if sa_model is None:
            raise HTTPException(404, f'No resource found with id {model_id}')
        return sa_model

    @staticmethod
    def check_ownership(request: Request, user: User) -> None:
        if request.user.admin:
            return
        if request.user.id != user.id:
            raise HTTPException(
                403, f'user {request.user.pseudo} does not have rights to edit this resource'
            )


class ErrorSchemaMixin:
    @staticmethod
    def handle_error(exc: ValidationError, data: dict, **_) -> None:
        if '_schema' in exc.messages:
            exc.messages['schema'] = exc.messages.pop('_schema')
        raise BadRequestError({
            'input': data,
            'errors': exc.messages
        })
