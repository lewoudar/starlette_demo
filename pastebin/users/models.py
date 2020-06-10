import bcrypt
from sqlalchemy import Column, String, Boolean, Table, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from sqlalchemy_utils import EmailType

from pastebin.meta import Base

user_groups = Table(
    'user_groups', Base.metadata,
    Column('user_id', ForeignKey('users.id'), primary_key=True),
    Column('group_id', ForeignKey('groups.id'), primary_key=True),
    Column('created_at', DateTime, default=func.now(), nullable=False)
)

group_permissions = Table(
    'group_permissions', Base.metadata,
    Column('group_id', ForeignKey('groups.id'), primary_key=True),
    Column('permission_id', ForeignKey('permissions.id'), primary_key=True),
    Column('created_at', DateTime, default=func.now(), nullable=False)
)


class User(Base):
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    pseudo = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(EmailType, unique=True, index=True, nullable=False)
    password_hash = Column(String(200), name='password', nullable=False)
    admin = Column(Boolean, nullable=False, default=False)
    # many to many User<->Group
    groups = relationship('Group', secondary=user_groups, back_populates='users')
    # non orm property useful for authentication
    is_authenticated = False

    def set_password(self, pw):
        _hash = bcrypt.hashpw(pw.encode('utf8'), bcrypt.gensalt())
        self.password_hash = _hash.decode('utf8')

    def check_password(self, pw):
        if self.password_hash is not None:
            expected_hash = self.password_hash.encode('utf8')
            return bcrypt.checkpw(pw.encode('utf8'), expected_hash)
        return False


class Group(Base):
    name = Column(String(100), nullable=False)
    # many to many Group<->User
    users = relationship('User', secondary=user_groups, back_populates='groups')
    # many to many Group<->Permission
    permissions = relationship('Permission', secondary=group_permissions, back_populates='groups')


class Permission(Base):
    name = Column(String(100), nullable=False)
    # many to many Permission<->Group
    groups = relationship('Group', secondary=group_permissions, back_populates='permissions')
