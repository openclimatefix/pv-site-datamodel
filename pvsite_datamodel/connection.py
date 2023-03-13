"""Database Connection class."""
import logging

from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Database connection class."""

    def __init__(self, url: URL | str, echo: bool = True):
        """Set up database connection.

        :param url: the database url, used for connecting
        :param echo: whether to echo
        """
        self.url = url
        self.engine = create_engine(self.url, echo=echo)
        self.Session = sessionmaker(bind=self.engine)
        if self.url is None:
            raise Exception("Need to set url for database connection")

    def get_session(self) -> Session:
        """Get sqlalchemy session."""
        return self.Session()
