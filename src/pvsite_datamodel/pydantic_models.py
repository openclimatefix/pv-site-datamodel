"""Pydantic models."""

from datetime import datetime
from uuid import UUID

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


class PVSiteEditMetadata(BaseModel):
    """Site metadata when editing a site."""

    client_site_id: int | None = Field(
        None,
        description="The site ID as given by the providing user.",
    )
    client_site_name: str | None = Field(
        None,
        description="The name of the site as given by the providing user.",
    )
    orientation: float | None = Field(
        None,
        description="The rotation of the panel in degrees. 180° points south",
    )
    tilt: float | None = Field(
        None,
        description="The tile of the panel in degrees. 90° indicates the panel is vertical.",
    )
    latitude: float | None = Field(None, description="The site's latitude", ge=-90, le=90)
    longitude: float | None = Field(None, description="The site's longitude", ge=-180, le=180)
    inverter_capacity_kw: float | None = Field(
        None,
        description="The site's inverter capacity in kw",
        ge=0,
    )
    module_capacity_kw: float | None = Field(
        None,
        description="The site's PV module nameplate capacity in kw",
        ge=0,
    )
    capacity_kw: float | None = Field(None, description="The site's total capacity in kw", ge=0)
    dno: str | None = Field(None, description="The site's DNO")
    gsp: str | None = Field(None, description="The site's GSP")
    client_uuid: UUID | None = Field(
        None,
        description="The UUID of the client this site belongs to",
    )
