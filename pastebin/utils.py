"""Module that contain some helper functions"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def get_session(database_url):
    engine = create_engine(database_url, connect_args={'check_same_thread': False})
    session_class = sessionmaker(bind=engine)
    return session_class()
