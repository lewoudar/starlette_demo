import asyncio
import code
import json
from pathlib import Path

import click
import transaction
import websockets
from pygments import highlight
from pygments.formatters import get_formatter_by_name
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from sqlalchemy import create_engine
from sqlalchemy_utils import create_database, database_exists
from zope.sqlalchemy import register

import pastebin
from pastebin.meta import Base
from pastebin.settings import REAL_DATABASE_URL, DEFAULT_USER_GROUP, DEFAULT_PERMISSIONS
from pastebin.snippets.models import Language, Style, LANGUAGES, STYLES
from pastebin.users.models import User, Group, Permission
from pastebin.utils import get_session


@click.group()
def cli():
    """Pastebin CLI manager"""


@cli.command('init-db')
@click.option('-u', '--url', help='database url used by sqlalchemy')
def initialize_database(url):
    """Creates the database if it does not exist"""
    database_url = REAL_DATABASE_URL if url is None else url
    if database_exists(database_url):
        click.secho(f'skipping creation of database {database_url} because it already exist', fg='blue')
    else:
        create_database(database_url)
        click.secho(f'created database {database_url}', fg='green')
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    click.echo('finished initialization')


@cli.command()
def shell():
    """Creates a python interpreter to interact with pastebin modules"""
    db = get_session(REAL_DATABASE_URL)
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
    db = get_session(REAL_DATABASE_URL)
    register(db, transaction_manager=transaction.manager)
    with transaction.manager:
        user = User(email=email, pseudo=pseudo, first_name=first_name, last_name=last_name, admin=True)
        user.set_password(password)
        default_group = db.query(Group).filter_by(name=DEFAULT_USER_GROUP).one_or_none()
        if default_group is None:
            default_group = Group(name=DEFAULT_USER_GROUP)
            for name in DEFAULT_PERMISSIONS:
                default_group.permissions.append(Permission(name=name))
        user.groups.append(default_group)
        db.add(user)
    db.close()
    click.secho(f'created admin user {pseudo}!', fg='green')


@cli.command('add-lang-to-db')
def add_languages_to_db():
    """Add supported pygments languages to the database"""
    db = get_session(REAL_DATABASE_URL)
    register(db, transaction_manager=transaction.manager)
    with transaction.manager:
        for lang in LANGUAGES:
            language = Language(name=lang)
            db.add(language)
    db.close()
    click.secho('successfully inserted languages to the database!', fg='green')


@cli.command('add-styles-to-db')
def add_styles_to_db():
    """Add supported pygments styles to the database"""
    db = get_session(REAL_DATABASE_URL)
    register(db, transaction_manager=transaction.manager)
    with transaction.manager:
        for item in STYLES:
            style = Style(name=item)
            db.add(style)
    db.close()
    click.secho('successfully inserted styles to the database!', fg='green')


@cli.command('highlight-css')
def highlight_css():
    """Create css file style.css in pastebin/static/css folder"""
    static_path = Path(__file__).parent.parent.parent / 'static'
    click.echo(f'{static_path.absolute()}')
    css_path = static_path / 'css'
    if not static_path.exists():
        css_path.mkdir(parents=True, exist_ok=True)
        click.echo('created static folder with a chidl css folder')

    if not static_path.is_dir():
        raise click.UsageError('pastebin/static path exists and it is not a folder, please change it')

    if not css_path.exists():
        css_path.mkdir()
        click.echo('created static/css folder')
    style_path = css_path / 'style.css'
    style_path.write_text(HtmlFormatter().get_style_defs('.highlight'))
    click.secho('static/css/style.css file was successfully created!', fg='green')


@cli.command()
@click.option('-u', '--url', default='ws://localhost:8000/feed')
def feed(url):
    """Print websocket information when an event happens in the application."""

    async def _feed(uri):
        lexer = get_lexer_by_name('json')
        formatter = get_formatter_by_name('console')
        click.secho('listening for events\n', fg='blue')
        try:
            async with websockets.connect(uri) as websocket:
                while True:
                    data = json.loads(await websocket.recv())
                    click.echo(highlight(json.dumps(data, indent=4), lexer, formatter))
                    click.echo('==NEXT EVENT==\n')
        except websockets.WebSocketException as e:
            click.echo(e)

    asyncio.run(_feed(url))
