from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse


def http_exception(_, exc: HTTPException) -> JSONResponse:
    return JSONResponse({'detail': exc.detail}, status_code=exc.status_code)


class ClientError(Exception):
    """
    Starlette exception uses a string for detail which I don't think is handful for marshmallow errors,
    so I implemented a slight different version where detail is a dict.
    """

    def __init__(self, status_code: int, detail: dict):
        self.status_code = status_code
        self.detail = detail

    def __repr__(self):
        class_name = self.__class__.__name__
        return f'{class_name}(status_code={self.status_code!r}, detail={self.detail!r})'


def client_error(_, exc: ClientError) -> JSONResponse:
    return JSONResponse({'detail': exc.detail}, status_code=exc.status_code)


class BadRequestError(ClientError):
    def __init__(self, detail: dict):
        super().__init__(400, detail)
