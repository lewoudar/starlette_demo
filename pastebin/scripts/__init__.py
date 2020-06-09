import code

import click
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, database_exists

from pastebin.meta import Base
from pastebin.settings import DATABASE_URL
from pastebin.users.models import User, Group, Permission


def initialize_database():
    """Creates the database if it does not exist"""
    database_url = DATABASE_URL
    click.echo(database_url)
    if database_exists(database_url):
        click.secho(f'skipping creation of database {database_url} because it already exist', fg='blue')
    else:
        create_database(database_url)
        click.secho(f'created database {database_url}', fg='green')
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    click.echo('finished initialization')


def shell():
    """Creates a python interpreter with sqlalchemy models"""
    engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False})
    session_class = sessionmaker(bind=engine)
    db = session_class()
    code.interact(banner='Interactive database console', exitmsg='Good bye!', local={
        'User': User,
        'Group': Group,
        'Permission': Permission,
        'db': db
    })
    db.close()
