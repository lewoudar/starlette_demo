import pytest
import transaction
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient
from sqlalchemy_utils import database_exists, create_database, drop_database
from zope.sqlalchemy import register

from pastebin import app
from pastebin.users.models import Base
from pastebin.settings import TEST_DATABASE_URL
from .utils import create_test_objects


@pytest.fixture(scope='session', autouse=True)
def create_test_database():
    """
    Create a clean database on every test case.
    For safety, we should abort if a database already exists.
    """
    assert not database_exists(TEST_DATABASE_URL), 'Test database already exists. Aborting tests.'
    create_database(TEST_DATABASE_URL)
    engine = create_engine(TEST_DATABASE_URL, connect_args={'check_same_thread': False})
    session_class = sessionmaker(bind=engine)
    db = session_class()
    register(db, transaction_manager=transaction.manager)
    Base.metadata.create_all(engine)
    create_test_objects(db)
    yield
    drop_database(TEST_DATABASE_URL)


@pytest.fixture()
def client():
    """Test client."""
    with TestClient(app) as client:
        yield client
