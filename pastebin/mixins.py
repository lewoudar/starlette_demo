from starlette.exceptions import HTTPException
from starlette.requests import Request

from .meta import Base as Model


class SAModelMixin:

    @staticmethod
    def get_model_by_id(request: Request, model: Model, model_id: int) -> Model:
        sa_model = request.state.db.query(model).filter(model.id == model_id).one_or_none()
        if sa_model is None:
            raise HTTPException(404, f'No resource found with id {model_id}')
        return sa_model
