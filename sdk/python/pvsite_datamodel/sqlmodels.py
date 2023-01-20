"""
SQLAlchemy definition of the pvsite database schema
"""

import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import FLOAT, INTEGER, REAL, TIMESTAMP, UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy import Column, DateTime

Base = declarative_base()


class CreatedMixin:
    """Mixin to add created datetime to model"""

    created_utc = Column(DateTime(timezone=True), default=lambda: datetime.utcnow())


class SiteSQL(Base, CreatedMixin):
    """
    Class representing the sites table.

    Each site row specifies a single panel or cluster of panels
    found on a residential house or commercial building. Their
    data is provided by a client.

    *Approximate size: *
    4 clients * ~1000 sites each = ~4000 rows
    """

    __tablename__ = "sites"

    site_uuid = sa.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    client_uuid = sa.Column(
        UUID(as_uuid=True), sa.ForeignKey("clients.client_uuid"), nullable=False, default=uuid.uuid4
    )
    client_site_id = sa.Column(INTEGER)
    client_site_name = sa.Column(sa.String(255))
    region = sa.Column(sa.String(255))
    dno = sa.Column(sa.String(255))
    gsp = sa.Column(sa.String(255))
    orientation = sa.Column(REAL)
    tilt = sa.Column(REAL)
    latitude = sa.Column(FLOAT, nullable=False)
    longitude = sa.Column(FLOAT, nullable=False)
    capacity_kw = sa.Column(REAL, nullable=False)
    updated_utc = sa.Column(TIMESTAMP, nullable=False, default=lambda: datetime.utcnow())
    ml_id = sa.Column(sa.Integer, autoincrement=True, nullable=False, unique=True)

    __table_args__ = (UniqueConstraint("client_site_id", client_uuid, name="idx_client"),)

    forecasts = relationship("ForecastSQL")
    latest_forecast_values = relationship("LatestForecastValueSQL")
    generation = relationship("GenerationSQL")


class GenerationSQL(Base, CreatedMixin):
    """
    Class representing the generation table.

    Each generation row specifies a generated power output over a
    given time range for a site.

    *Approximate size: *
    Generation populated every 5 minutes per site * 4000 sites = ~1,125,000 rows per day
    """

    __tablename__ = "generation"

    generation_uuid = sa.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    site_uuid = sa.Column(
        UUID(as_uuid=True), sa.ForeignKey("sites.site_uuid"), nullable=False, default=uuid.uuid4
    )
    power_kw = sa.Column(REAL, nullable=False)
    datetime_interval_uuid = sa.Column(
        UUID(as_uuid=True),
        sa.ForeignKey("datetime_intervals.datetime_interval_uuid"),
        nullable=False,
        default=uuid.uuid4,
    )


class ForecastSQL(Base, CreatedMixin):
    """
    Class representing the forecasts table.

    Each forecast row refers to a sequence of predicted solar generation values
    over a set of target times for a site.

    *Approximate size: *
    One forecast per site every 5 minutes = ~1,125,000 rows per day
    """

    __tablename__ = "forecasts"

    forecast_uuid = sa.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    site_uuid = sa.Column(
        UUID(as_uuid=True), sa.ForeignKey("sites.site_uuid"), nullable=False, default=uuid.uuid4
    )

    forecast_version = sa.Column(sa.String(32), nullable=False)

    # one (forecasts) to many (forecast_values)
    forecast_values = relationship("ForecastValueSQL")


class ForecastValueSQL(Base, CreatedMixin):
    """
    Class representing the forecast_values table.

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
    datetime_interval_uuid = sa.Column(
        UUID(as_uuid=True),
        sa.ForeignKey("datetime_intervals.datetime_interval_uuid"),
        nullable=False,
        default=uuid.uuid4,
    )
    forecast_generation_kw = sa.Column(REAL, nullable=False)

    forecast_uuid = sa.Column(
        UUID(as_uuid=True),
        sa.ForeignKey("forecasts.forecast_uuid"),
        nullable=False,
        default=uuid.uuid4,
    )


class LatestForecastValueSQL(Base, CreatedMixin):
    """
    Class representing the latest_forecast_values table.

    Each latest_forecast_value row is a prediction for the power output
    of a site over a target datetime interval. Only the most recent
    prediction for each target time interval is stored in this table
    per site.

    *Approximate size: *
    One forecast value every 5 minutes per site per forecast
    sequence = ~1,125,000 rows per day
    """

    __tablename__ = "latest_forecast_values"

    latest_forecast_value_uuid = sa.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    datetime_interval_uuid = sa.Column(
        UUID(as_uuid=True),
        sa.ForeignKey("datetime_intervals.datetime_interval_uuid"),
        nullable=False,
        default=uuid.uuid4,
    )
    forecast_generation_kw = sa.Column(REAL, nullable=False)

    forecast_uuid = sa.Column(UUID(as_uuid=True), default=uuid.uuid4, nullable=False)
    site_uuid = sa.Column(
        UUID(as_uuid=True), sa.ForeignKey("sites.site_uuid"), nullable=False, default=uuid.uuid4
    )
    forecast_version = sa.Column(sa.String(32), nullable=False)

    latest_forecast = relationship("SiteSQL", back_populates="latest_forecast_values")


class ClientSQL(Base, CreatedMixin):
    """
    Class representing the clients table.

    Each client row defines a provider of site data

    *Approximate size: *
    One row per client = ~4 rows
    """

    __tablename__ = "clients"

    client_uuid = sa.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    client_name = sa.Column(sa.String(255), nullable=False)

    sites = relationship("SiteSQL")


class DatetimeIntervalSQL(Base, CreatedMixin):
    """
    Class representing the datetime_intervals table.

    Each datetime_interval row defines a timespan between a start and end time

    *Approximate size: *
    One interval every 5 minutes per day = ~288 rows per day
    """

    __tablename__ = "datetime_intervals"

    datetime_interval_uuid = sa.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    start_utc = sa.Column(TIMESTAMP, nullable=False)
    end_utc = sa.Column(TIMESTAMP, nullable=False)

    generation = relationship("GenerationSQL")
    forecast_values = relationship("ForecastValueSQL")
    latest_forecast_values = relationship("LatestForecastValueSQL")


class StatusSQL(Base, CreatedMixin):
    """
    Class representing the status table:

    Each status row defines a message reporting on the status of the
    services within the nowcasting domain

    *Approximate size: *
    ~1 row per day
    """

    __tablename__ = "status"

    status_uuid = sa.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    status = sa.Column(sa.String(255))
    message = sa.Column(sa.String(255))
