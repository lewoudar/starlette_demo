import click
from sqlalchemy import create_engine
from sqlalchemy_utils import create_database, database_exists

from pastebin.meta import Base
from pastebin.settings import DATABASE_URL


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
