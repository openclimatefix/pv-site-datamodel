"""Cross-package functions."""

import datetime as dt
import typing

from pvsite_datamodel.sqlmodels import Base


class WrittenRow(typing.NamedTuple):
    """Defines a write to the Database."""

    table: Base
    pk_value: str


FORECAST_TIMESPAN = dt.timedelta(minutes=5)
