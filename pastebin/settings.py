from pathlib import Path
from starlette.config import Config

env_path = Path(__file__).parent / '.env'
config = Config(f'{env_path.absolute()}')

DEBUG = config('DEBUG', cast=bool, default=False)
DATABASE_URL = config('DATABASE_URL', default='sqlite:///:memory:')
TESTING = config('TESTING', cast=bool, default=False)
TEST_DATABASE_URL = 'sqlite:///./test.db'
