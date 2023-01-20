"""
Schemas and validation for dataframes used in the package
"""

import uuid

import pandera as pa
from pandera.dtypes import Bool, DateTime, Float, String
from pandera.typing import Series


class InputForecastValuesSchema(pa.SchemaModel):
    """Schema defining the makeup of the input forecast values dataframe"""

    target_datetime_utc: Series[DateTime] = pa.Field()
    forecast_kw: Series[Float] = pa.Field(ge=0)
    pv_uuid: Series[String] = pa.Field(le=32)

    @pa.check("pv_uuid")
    def pv_uuid_check(cls, series: Series[String]) -> Series[Bool]:
        """Check that pv_uuid column values are valid uuids"""
        try:
            uuid.UUID(series.str, version=4)
        except ValueError:
            return False
        return True
