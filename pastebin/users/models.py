import bcrypt
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy_utils import EmailType

from pastebin.meta import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    pseudo = Column(String)
    email = Column(EmailType)
    password_hash = Column(Text, name='password')

    def set_password(self, pw):
        _hash = bcrypt.hashpw(pw.encode('utf8'), bcrypt.gensalt())
        self.password_hash = _hash.decode('utf8')

    def check_password(self, pw):
        if self.password_hash is not None:
            expected_hash = self.password_hash.encode('utf8')
            return bcrypt.checkpw(pw.encode('utf8'), expected_hash)
        return False
