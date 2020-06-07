from starlette.routing import Route
from .views import Users, UserInfo

routes = [
    Route('/', Users, name='user_list'),
    Route('/{id:int}', UserInfo, name='user_detail')
]
