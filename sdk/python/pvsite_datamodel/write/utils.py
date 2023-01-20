import datetime as dt
import typing

from pvsite_datamodel import sqlmodels


class WrittenRow(typing.NamedTuple):
    """
    Defines a write to the Database
    """

    table: sqlmodels.Base
    pk_value: str


FORECAST_TIMESPAN = dt.timedelta(minutes=5)