import bcrypt
from sqlalchemy import Column, String, Text
from sqlalchemy_utils import EmailType

from pastebin.meta import Base


class User(Base):
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    pseudo = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(EmailType, unique=True, index=True, nullable=False)
    password_hash = Column(Text, name='password', nullable=False)

    def set_password(self, pw):
        _hash = bcrypt.hashpw(pw.encode('utf8'), bcrypt.gensalt())
        self.password_hash = _hash.decode('utf8')

    def check_password(self, pw):
        if self.password_hash is not None:
            expected_hash = self.password_hash.encode('utf8')
            return bcrypt.checkpw(pw.encode('utf8'), expected_hash)
        return False
