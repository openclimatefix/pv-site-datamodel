""" Database Connection class"""
import logging

from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Database connection class"""

    def __init__(self, url: URL | str, echo: bool = True):
        """
        Set up database connection

        url: the database url, used for connecting
        """
        self.url = url
        self.engine = create_engine(self.url, echo=echo)
        self.Session = sessionmaker(bind=self.engine)
        assert self.url is not None, Exception("Need to set url for database connection")

    def get_session(self) -> Session:
        """Get sqlalamcy session"""
        return self.Session()
