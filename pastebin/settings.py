from pathlib import Path

from starlette.config import Config

env_path = Path(__file__).parent / '.env'
config = Config(f'{env_path.absolute()}')

DEBUG = config('DEBUG', cast=bool, default=False)
REAL_DATABASE_URL = config('REAL_DATABASE_URL', default='sqlite:///:memory:')
TESTING = config('TESTING', cast=bool, default=False)
TEST_DATABASE_URL = 'sqlite:///./test.db'
DATABASE_URL = TEST_DATABASE_URL if TESTING else REAL_DATABASE_URL
DEFAULT_USER_GROUP = config('DEFAULT_USER_GROUP')
DEFAULT_PERMISSIONS = ['users:read', 'users:write', 'snippets:read', 'snippets:write']
