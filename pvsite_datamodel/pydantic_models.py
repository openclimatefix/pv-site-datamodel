""" Pydantic models."""
from datetime import datetime

from pydantic import BaseModel, Field


class GenerationSum(BaseModel):
    """Sum of generation."""

    power_kw: float = Field(..., description="Summed power in kW")
    start_utc: datetime = Field(..., description="Start datetime of this power")
    name: str = Field(..., description="Name of item sums. ")


class ForecastValueSum(BaseModel):
    """Sum of forecast values."""

    power_kw: float = Field(..., description="Summed power in kW")
    start_utc: datetime = Field(..., description="Start datetime of this power")
    name: str = Field(..., description="Name of item sums. ")


class LatitudeLongitudeLimits(BaseModel):
    """Lat and lon limits."""

    latitude_min: float = Field(-90, description="Minimum latitude")
    latitude_max: float = Field(90, description="Maximum latitude")
    longitude_min: float = Field(-180, description="Minimum longitude")
    longitude_max: float = Field(180, description="Maximum longitude")
