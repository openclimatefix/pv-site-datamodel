"""Cross-package functions."""

import datetime as dt
import typing
import uuid
from typing import Iterable, Optional, Union

import pandas as pd
import pandera as pa

from pvsite_datamodel.sqlmodels import Base


class WrittenRow(typing.NamedTuple):
    """Defines a write to the Database."""

    table: Base
    pk_value: str


# Defines the length a forecast is valid for
FORECAST_TIMESPAN = dt.timedelta(minutes=5)


@pa.engines.pandas_engine.Engine.register_dtype
@pa.dtypes.immutable
class UUIDV4(pa.engines.pandas_engine.NpString):
    """Logical pandera datatype representation of a UUID version 4.

    Checks that the containing string can be cast as a uuidv4.
    https://pandera.readthedocs.io/en/stable/dtypes.html#logical-data-types
    """

    def check(
            self,
            pandera_dtype: pa.dtypes.DataType,
            data_container: Optional[pd.Series] = None,
    ) -> Union[bool, Iterable[bool]]:
        """Check validity of column and entries within."""
        # ensure that the data container's data type is a string,
        # using the parent class's check implementation
        correct_type = super().check(pandera_dtype)
        if not correct_type:
            return correct_type

        def _is_valid_uuidv4(s: str) -> bool:
            """Return True if s is valid UUID v4, False elsewise."""
            try:
                uuid.UUID(str(s), version=4)
                return True
            except ValueError:
                return False

        # ensure the strings are representations of valid UUIDv4s
        return data_container.map(lambda x: _is_valid_uuidv4(x))

    def __str__(self) -> str:
        """Get string representation of class."""
        return str(self.__class__.__name__)

    def __repr__(self) -> str:
        """Object type."""
        return f"DataType({self})"
