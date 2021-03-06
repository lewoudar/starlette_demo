from datetime import datetime

import transaction
from sqlalchemy.orm import Session

from pastebin.settings import DEFAULT_USER_GROUP, DEFAULT_PERMISSIONS
from pastebin.snippets.models import Language, Style, LANGUAGES, STYLES, Snippet
from pastebin.users.models import User, Group, Permission


# noinspection PyArgumentList
def create_test_objects(db: Session):
    with transaction.manager:
        # users
        user_date = datetime(year=2020, month=6, day=7, hour=16, minute=0, second=0)
        snippet_date = datetime(year=2020, month=6, day=28, hour=12, minute=35, second=0)
        kevin_user = User(first_name='Kevin', last_name='Tewouda', pseudo='lewoudar', email='kevin@gmail.com',
                          created_at=user_date)
        kevin_user.set_password('bar')
        admin_user = User(first_name='John', last_name='Doe', pseudo='admin', email='johnd@gmail.com', admin=True,
                          created_at=user_date)
        admin_user.set_password('admin')
        # group and permissions
        default_group = Group(name=DEFAULT_USER_GROUP)
        for name in DEFAULT_PERMISSIONS:
            default_group.permissions.append(Permission(name=name))
        kevin_user.groups.append(default_group)
        admin_user.groups.append(default_group)
        # we add a snippet to kevin user
        kevin_user.snippets = [
            Snippet(title='first snippet', code='print("hello world!")', linenos=True, language='python',
                    style='friendly', created_at=snippet_date)
        ]
        db.add_all([kevin_user, admin_user, default_group])

        # languages
        for lang in LANGUAGES:
            language = Language(name=lang)
            db.add(language)
        # styles
        for name in STYLES:
            style = Style(name=name)
            db.add(style)


def assert_in_dict(dict1: dict, dict2: dict):
    for key in dict1:
        assert key in dict2
        assert dict1[key] == dict2[key]
