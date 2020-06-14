"""This module contains an implementation of an HTTP basic authentication backend"""
import base64
import binascii

from starlette.authentication import AuthenticationBackend, AuthenticationError, AuthCredentials
from starlette.responses import JSONResponse

from pastebin.settings import DATABASE_URL
from pastebin.users.models import User
from pastebin.utils import get_session


class BasicAuthBackend(AuthenticationBackend):
    async def authenticate(self, request):
        if 'Authorization' not in request.headers:
            return

        auth = request.headers['Authorization']
        try:
            scheme, credentials = auth.split()
            if scheme.lower() != 'basic':
                return
            decoded = base64.b64decode(credentials).decode("ascii")
        except (ValueError, UnicodeDecodeError, binascii.Error):
            raise AuthenticationError('Invalid basic auth credentials')

        pseudo, _, password = decoded.partition(':')
        db = get_session(DATABASE_URL)
        user = db.query(User).filter(User.pseudo == pseudo).one_or_none()
        if user is None or not user.check_password(password):
            db.close()
            raise AuthenticationError(f'pseudo or password incorrect')

        user.is_authenticated = True
        scopes = ['authenticated']
        for group in user.groups:
            scopes.extend([permission.name for permission in group.permissions])
        db.close()
        return AuthCredentials(scopes), user


def on_auth_error(_, exc: Exception):
    return JSONResponse({'detail': str(exc)}, status_code=401)
