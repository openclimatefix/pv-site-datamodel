"""SQLAlchemy definition of the pvsite database schema."""

from __future__ import annotations

# This means we can use Typing of objects that have jet to be defined
import uuid
from datetime import datetime
from typing import List

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.schema import UniqueConstraint

Base = declarative_base()


class CreatedMixin:
    """Mixin to add created datetime to model."""

    created_utc = sa.Column(sa.DateTime, default=lambda: datetime.utcnow())


class SiteSQL(Base, CreatedMixin):
    """Class representing the sites table.

    Each site row specifies a single panel or cluster of panels
    found on a residential house or commercial building. Their
    data is provided by a client.

    *Approximate size: *
    4 clients * ~1000 sites each = ~4000 rows
    """

    __tablename__ = "sites"

    site_uuid = sa.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    client_uuid = sa.Column(
        UUID(as_uuid=True),
        sa.ForeignKey("clients.client_uuid"),
        nullable=False,
    )
    client_site_id = sa.Column(sa.Integer, index=True)
    client_site_name = sa.Column(sa.String(255), index=True)

    region = sa.Column(sa.String(255))
    dno = sa.Column(sa.String(255))
    gsp = sa.Column(sa.String(255))

    # For metadata `NULL` means "we don't know".
    orientation = sa.Column(sa.Float)
    tilt = sa.Column(sa.Float)
    latitude = sa.Column(sa.Float)
    longitude = sa.Column(sa.Float)
    capacity_kw = sa.Column(sa.Float)

    ml_id = sa.Column(sa.Integer, autoincrement=True, nullable=False, unique=True)

    __table_args__ = (UniqueConstraint("client_site_id", client_uuid, name="idx_client"),)

    forecasts: List["ForecastSQL"] = relationship("ForecastSQL")
    generation: List["GenerationSQL"] = relationship("GenerationSQL")
    client: ClientSQL = relationship("ClientSQL", back_populates="sites")


class GenerationSQL(Base, CreatedMixin):
    """Class representing the generation table.

    Each generation row specifies a generated power output over a
    given time range for a site.

    *Approximate size: *
    Generation populated every 5 minutes per site * 4000 sites = ~1,125,000 rows per day
    """

    __tablename__ = "generation"
    __table_args__ = (
        UniqueConstraint("site_uuid", "start_utc", "end_utc", name="uniq_cons_site_start_end"),
    )

    generation_uuid = sa.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    site_uuid = sa.Column(
        UUID(as_uuid=True),
        sa.ForeignKey("sites.site_uuid"),
        nullable=False,
        index=True,
    )
    generation_power_kw = sa.Column(sa.Float, nullable=False)

    start_utc = sa.Column(sa.DateTime, nullable=False, index=True)
    end_utc = sa.Column(sa.DateTime, nullable=False)

    site: SiteSQL = relationship("SiteSQL", back_populates="generation")


class ForecastSQL(Base, CreatedMixin):
    """Class representing the forecasts table.

    Each forecast row refers to a sequence of predicted solar generation values
    over a set of target times for a site.

    *Approximate size: *
    One forecast per site every 5 minutes = ~1,125,000 rows per day
    """

    __tablename__ = "forecasts"

    forecast_uuid = sa.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    site_uuid = sa.Column(
        UUID(as_uuid=True),
        sa.ForeignKey("sites.site_uuid"),
        nullable=False,
        index=True,
    )

    forecast_version = sa.Column(sa.String(32), nullable=False)

    # one (forecasts) to many (forecast_values)
    forecast_values: List["ForecastValueSQL"] = relationship("ForecastValueSQL")


class ForecastValueSQL(Base, CreatedMixin):
    """Class representing the forecast_values table.

    Each forecast_value row is a prediction for the power output
    of a site over a target datetime interval. Many predictions
    are made for each site at each target interval.

    *Approximate size: *
    One forecast value every 5 minutes per site per forecast.
    Each forecast's prediction sequence covers 24 hours of target
    intervals = ~324,000,000 rows per day
    """

    __tablename__ = "forecast_values"

    forecast_value_uuid = sa.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)

    start_utc = sa.Column(sa.DateTime, nullable=False, index=True)
    end_utc = sa.Column(sa.DateTime, nullable=False)
    forecast_power_kw = sa.Column(sa.Float, nullable=False)

    forecast_uuid = sa.Column(
        UUID(as_uuid=True),
        sa.ForeignKey("forecasts.forecast_uuid"),
        nullable=False,
        index=True,
    )

    # This is redundant from the Forecast table, but it means we can save a JOIN for a very frequent
    # query, which is getting forecasts for given sites.
    site_uuid = sa.Column(
        UUID(as_uuid=True),
        sa.ForeignKey("sites.site_uuid"),
        nullable=False,
        index=True,
    )

    forecast: ForecastSQL = relationship("ForecastSQL", back_populates="forecast_values")


class ClientSQL(Base, CreatedMixin):
    """Class representing the clients table.

    Each client row defines a provider of site data

    *Approximate size: *
    One row per client = ~4 rows
    """

    __tablename__ = "clients"

    client_uuid = sa.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    client_name = sa.Column(sa.String(255), nullable=False)

    sites: List[SiteSQL] = relationship("SiteSQL")


class StatusSQL(Base, CreatedMixin):
    """Class representing the status table.

    Each status row defines a message reporting on the status of the
    services within the nowcasting domain

    *Approximate size: *
    ~1 row per day
    """

    __tablename__ = "status"

    status_uuid = sa.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    status = sa.Column(sa.String(255))
    message = sa.Column(sa.String(255))
