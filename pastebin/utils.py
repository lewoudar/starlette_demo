"""Module that contain some helper functions"""
import asyncio
import typing
from enum import Enum, auto

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

CHANNELS: typing.Set[asyncio.Queue] = set()


class Operation(Enum):
    CREATE = auto()
    UPDATE = auto()
    DELETE = auto()


class Model(Enum):
    USERS = auto()
    SNIPPETS = auto()


async def send_group(operation: Operation, model: Model, message: typing.Any) -> None:
    for channel in CHANNELS:
        await channel.put({'operation': operation.name, 'model': model.name.lower(), 'payload': message})


def get_session(database_url):
    engine = create_engine(database_url, connect_args={'check_same_thread': False})
    session_class = sessionmaker(bind=engine)
    return session_class()


def get_like_string(value: str) -> str:
    """
    Replaces character "*" by "%" and character "?" by "_"
    The new value will be used for sql search using LIKE construct.
    """
    return value.replace('?', '_').replace('*', '%')
