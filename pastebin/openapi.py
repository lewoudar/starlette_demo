from pathlib import Path

import yaml
from starlette.requests import Request
from starlette.responses import Response
from starlette.schemas import SchemaGenerator


def openapi_schema(request: Request) -> Response:
    path = Path(__file__).parent / 'openapi.yml'
    with path.open() as file:
        schema = SchemaGenerator(yaml.safe_load(file))

    return schema.OpenAPIResponse(request)
