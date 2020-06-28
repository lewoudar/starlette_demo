from starlette.routing import Route

from .views import get_languages, get_styles, Snippets

routes = [
    Route('/languages', get_languages, name='snippet_languages'),
    Route('/styles', get_styles, name='snippet_styles'),
    Route('/', Snippets, name='snippet_list')
]
