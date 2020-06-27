from starlette.routing import Route

from .views import get_languages, get_styles

routes = [
    Route('/languages', get_languages, name='snippet_languages'),
    Route('/styles', get_styles, name='snippet_styles')
]
