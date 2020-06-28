from pygments.lexers import get_all_lexers
from pygments.styles import get_all_styles
from sqlalchemy import Column, String, Text, Boolean, Enum, Integer, ForeignKey
from sqlalchemy.orm import relationship

from pastebin.meta import Base

LANGUAGES = sorted(set([item[1][0] for item in get_all_lexers()]))
STYLES = sorted([item for item in get_all_styles()])


class Language(Base):
    name = Column(String(100), nullable=False, unique=True, index=True)


class Style(Base):
    name = Column(String(100), nullable=False, unique=True, index=True)


class Snippet(Base):
    title = Column(String(100), nullable=False)
    code = Column(Text, nullable=False)
    linenos = Column(Boolean, nullable=False, default=False)
    language = Column(Enum(*LANGUAGES, name='language'), nullable=False)
    style = Column(Enum(*STYLES, name='style'), nullable=False, default='friendly')
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship('User', back_populates='snippets')
