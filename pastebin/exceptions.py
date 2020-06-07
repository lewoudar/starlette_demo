from starlette.responses import JSONResponse


def http_exception(_, exc):
    return JSONResponse({'detail': exc.detail}, status_code=exc.status_code)
