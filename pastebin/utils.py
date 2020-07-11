"""Module that contain some helper functions"""
import asyncio
from enum import Enum, auto
from typing import Any, List, Set, TypeVar, Optional, Dict

from marshmallow import Schema
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.requests import Request

from pastebin.snippets.models import Base
from .exceptions import ClientError
from .settings import ITEMS_PER_PAGE

CHANNELS: Set[asyncio.Queue] = set()
ModelClass = TypeVar('ModelClass')


class Operation(Enum):
    CREATE = auto()
    UPDATE = auto()
    DELETE = auto()


class Model(Enum):
    USERS = auto()
    SNIPPETS = auto()


async def send_group(operation: Operation, model: Model, message: Any) -> None:
    for channel in CHANNELS:
        await channel.put({'operation': operation.name, 'model': model.name.lower(), 'payload': message})


def get_session(database_url: str):
    engine = create_engine(database_url, connect_args={'check_same_thread': False})
    session_class = sessionmaker(bind=engine)
    return session_class()


def get_like_string(value: str) -> str:
    """
    Replaces character "*" by "%" and character "?" by "_"
    The new value will be used for sql search using LIKE construct.
    """
    return value.replace('?', '_').replace('*', '%')


class Paginator:

    def __init__(self, request: Request, model_class: ModelClass, schema: Schema):
        self.request = request
        self.model_class = model_class
        self.schema = schema
        self.current_page = int(self.request.query_params.get('page', 1))
        self.items = self.get_items()

    def get_items(self) -> List[Base]:
        if self.current_page <= 0:
            raise ClientError(400, detail={
                'input': {'url': f'{self.request.url}'},
                'error': 'page query parameter must be greater than 0'
            })
        left_index = (self.current_page - 1) * ITEMS_PER_PAGE
        right_index = self.current_page * ITEMS_PER_PAGE
        return self.request.state.db.query(self.model_class)[left_index:right_index]

    def get_previous_link(self) -> Optional[str]:
        if self.current_page == 1:
            return None
        else:
            url = f'{self.request.url}'.split('?')[0]
            return f'{url}?page={self.current_page - 1}'

    def get_next_link(self) -> Optional[str]:
        if len(self.items) < ITEMS_PER_PAGE:
            return None
        else:
            url = f'{self.request.url}'.split('?')[0]
            return f'{url}?page={self.current_page + 1}'

    def render(self) -> Dict[str, Any]:
        return {
            'previous': self.get_previous_link(),
            'next': self.get_next_link(),
            'items': self.schema.dump(self.items, many=True)
        }
