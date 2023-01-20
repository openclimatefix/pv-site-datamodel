import sqlalchemy as sa
from sqlalchemy import orm as sa_orm
from sqlalchemy.dialects import postgresql as sa_psql

from pvsite_datamodel import sqlmodels
from pvsite_datamodel.write.utils import WrittenRow


def upsert(session: sa_orm.Session, table: sqlmodels.Base, rows: list[dict]) -> list[WrittenRow]:
    """
    Upsert rows into table

    This functions checks the primary keys, and if present, updates the row.
    :param session: sqlalchemy Session
    :param table: the table
    :param rows: the rows we are going to update
    :return list[WrittenRow]: A list of WrittenRow objects containing the table and primary
    key values
    that have been written
    """

    # Input type validation in case user passes in a dict, not a list of dicts
    if type(rows) != list:
        if type(rows) == dict:
            rows = [rows]
        else:
            raise TypeError("input rows must be a list of dict objects")

    stmt = sa_psql.insert(table.__table__)
    primary_key_names = [key.name for key in sa.inspect(table.__table__).primary_key]
    update_dict = {c.name: c for c in stmt.excluded if not c.primary_key}

    if not update_dict:
        raise ValueError("insert_or_update resulted in an empty update_dict")

    stmt = stmt.on_conflict_do_update(index_elements=primary_key_names, set_=update_dict)
    session.execute(stmt, rows)
    session.commit()

    return [WrittenRow(table=table, pk_value=row[primary_key_names[0]]) for row in rows]