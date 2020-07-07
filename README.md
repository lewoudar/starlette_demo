# Pastebin api demo

This project aims to learn [starlette](https://www.starlette.io/) framework by reproducing
the [tutorial](https://www.django-rest-framework.org/tutorial/1-serialization/) of Django Rest Framework which
is an api where you can show some python code snippets.

## Installation
- Make sure you have python3.8 or upper installed.
- install [poetry](https://python-poetry.org/) if you don't have it. It is used for package dependencies and virtual environment.
- run `poetry install`. This will install all the dependencies.

Also you need to create .env ([12 factor app](https://12factor.net/config)) file for project configuration. There is a
sample file you can found in pastebin/env.sample. It must contain the following keys:
- **DEBUG**: with value `true` or `false`. This is to decide to print starlette debug information or not. It is a good idea
to turn this value to `true` when developing and `false` when your application is ready for production
- **TESTING**: with value `true` or `false`. This is to switch some variables during testing like the database url.
Something tricky with this variable is that it is easy to forget to change it when switching between tests and development.
So I ended up to not put it in the `.env` file and just configuration my Pycharm editor to set automatically `TESTING=true`
when testing and setting it by hand on my terminal to `TESTING=false` before launching the development server.
- **REAL_DATABASE_URL**: the absolute path to the database url. For this application, make sure it looks like
`sqlite:///absolute-path-to-starlette-demo/pastebin.db`. If you want to put the database in another folder, don't forget to update
`./pastebin/alembic.ini`, mainly you need to change the key `sqlalchemy.url` to the database path.
- **DEFAULT_USER_GROUP**: a string representing the group where common users will be placed. I just use `default_user` but you
can put whatever you want.


## CLI
For this project, I create a CLI to help me with scaffolding and tests. You can discover its features by running
`manage --help`

```bash
Usage: manage [OPTIONS] COMMAND [ARGS]...

  Pastebin CLI manager

Options:
  --help  Show this message and exit.

Commands:
  add-lang-to-db     Add supported pygments languages to the database
  add-styles-to-db   Add supported pygments styles to the database
  create-admin-user  Creates admin user
  feed               Print websocket information when an event happens in...
  highlight-css      Create css file style.css in pastebin/static/css folder
  init-db            Creates the database if it does not exist
  shell              Creates a python interpreter to interact with pastebin...
```

## Setting up the database
You need to setup the database, so you must run the following commands in starlette_demo folder:
- `manage init-db`: this command will create the database
- `manage create-admin-user`: this command will help you create an admin user, just enter the required information prompted.
It will also create a default user group if one does not exist.
- `manage add-lang-to-db` will populate the languages table. This is useful for route `GET /snippets/languages`.
- `manage add-styles-to-db` will populate the styles table. This is useful for route `GET /snippets/styles`.


## Running the api
First make sure environment variable `TESTING` is set to `false`.

After you can run `uvicorn pastebin:app`.

## Using the api
You can access the openapi specification on the following url: `http://localhost:8000/schema`.

Copy and paste the downloaded file on the openapi [editor](https://editor.swagger.io/) and you will see all available
operations.

The first operation you will need to do is create a user. After that you can play with snippets :)

### websocket feedback
For fun and learning purposes, I also add a websocket endpoint at ws://localhost:8000/feed. Each time a model is created,
updated or deleted, there is an information send to this endpoint. To see these information, you can launch a websocket
client with `manage feed`.