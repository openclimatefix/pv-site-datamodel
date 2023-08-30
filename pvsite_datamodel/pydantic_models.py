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
