from datetime import datetime
import transaction
from sqlalchemy.orm import Session

from pastebin.users.models import User


# noinspection PyArgumentList
def create_test_objects(db: Session):
    with transaction.manager:
        user_date = datetime(year=2020, month=6, day=7, hour=16, minute=0, second=0)
        user = User(first_name='Kevin', last_name='Tewouda', pseudo='lewoudar', email='foo@gmail.com',
                    created_at=user_date)
        user.set_password('bar')
        db.add(user)


def assert_in_dict(dict1: dict, dict2: dict):
    for key in dict1:
        assert key in dict2
        assert dict1[key] == dict2[key]
