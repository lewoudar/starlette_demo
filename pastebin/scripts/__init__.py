import code

import click
import transaction
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, database_exists
from zope.sqlalchemy import register

import pastebin
from pastebin.meta import Base
from pastebin.settings import DATABASE_URL
from pastebin.users.models import User


@click.group()
def cli():
    """Pastebin CLI manager"""


@cli.command('init-db')
@click.option('-u', '--url', help='database url used by sqlalchemy')
def initialize_database(url):
    """Creates the database if it does not exist"""
    database_url = DATABASE_URL if url is None else url
    if database_exists(database_url):
        click.secho(f'skipping creation of database {database_url} because it already exist', fg='blue')
    else:
        create_database(database_url)
        click.secho(f'created database {database_url}', fg='green')
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    click.echo('finished initialization')


def get_session(database_url):
    engine = create_engine(database_url, connect_args={'check_same_thread': False})
    session_class = sessionmaker(bind=engine)
    return session_class()


@cli.command()
def shell():
    """Creates a python interpreter to interact with pastebin modules"""
    db = get_session(DATABASE_URL)
    register(db, transaction_manager=transaction.manager)
    with transaction.manager:
        code.interact(banner='Interactive pastebin console', exitmsg='Good bye!', local={
            'pastebin': pastebin,
            'db': db,
            'transaction': transaction
        })
    db.close()


@cli.command('create-admin-user')
@click.option('-e', '--email', prompt='Email address', help='your email address')
@click.option('-f', '--first-name', prompt='First name', help='your first name')
@click.option('-l', '--last-name', prompt='Last name', help='your last name')
@click.password_option('-p', '--password', help='your user password')
@click.option('-P', '--pseudo', prompt='Pseudo', help='your pseudo or nickname')
def create_admin_user(first_name, last_name, pseudo, password, email):
    """Creates admin user"""
    db = get_session(DATABASE_URL)
    register(db, transaction_manager=transaction.manager)
    with transaction.manager:
        user = User(email=email, pseudo=pseudo, first_name=first_name, last_name=last_name, admin=True)
        user.set_password(password)
        db.add(user)
    db.close()
    click.secho(f'created admin user {pseudo}!', fg='blue')
