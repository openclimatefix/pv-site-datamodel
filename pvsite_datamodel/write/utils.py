"""
Useful functions for write operations.
"""

from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Session

from pvsite_datamodel.sqlmodels import Base


def _insert_do_nothing_on_conflict(session: Session, table: Base, rows: list[dict]):
    """Upserts rows into table.

    This functions checks the primary keys and constraints, and if present, does nothing
    :param session: sqlalchemy Session
    :param table: the table
    :param rows: the rows we are going to update
    """
    stmt = postgresql.insert(table.__table__)
    stmt = stmt.on_conflict_do_nothing()
    session.execute(stmt, rows)
