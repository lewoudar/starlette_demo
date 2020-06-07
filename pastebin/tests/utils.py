import transaction
from sqlalchemy.orm import Session

from pastebin.users.models import User


def create_test_objects(db: Session):
    with transaction.manager:
        user = User(first_name='Kevin', last_name='Tewouda', pseudo='lewoudar', email='foo@gmail.com')
        user.set_password('bar')
        db.add(user)
