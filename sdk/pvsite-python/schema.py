import uuid

import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID, REAL, FLOAT, INTEGER, TIMESTAMP
from sqlalchemy.schema import UniqueConstraint

Base = declarative_base()


class SiteSQL(Base):
    __tablename__ = 'sites'

    site_uuid = sa.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    client_uuid = sa.Column(UUID(as_uuid=True), sa.ForeignKey('clients.client_uuid'), nullable=False, default=uuid.uuid4)
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
    created_utc = sa.Column(TIMESTAMP, nullable=False)
    updated_utc = sa.Column(TIMESTAMP, nullable=False)
    ml_id = sa.Column(sa.Integer, autoincrement=True, nullable=False, unique=True)

    __table_args__ = (
        UniqueConstraint("client_site_id", client_uuid, name='idx_client'),
    )

    forecasts = relationship("ForecastSQL")
    latest_forecast_values = relationship("LatestForecastValueSQL")
    generation = relationship("GenerationSQL")


class GenerationSQL(Base):
    __tablename__ = 'generation'

    generation_uuid = sa.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    site_uuid = sa.Column(UUID(as_uuid=True), sa.ForeignKey('sites.site_uuid'), nullable=False, default=uuid.uuid4)
    power_kw = sa.Column(REAL, nullable=False)
    datetime_interval_uuid = sa.Column(UUID(as_uuid=True), sa.ForeignKey('datetime_intervals.datetime_interval_uuid'), nullable=False, default=uuid.uuid4)
    created_utc = sa.Column(TIMESTAMP, nullable=False)


class ForecastSQL(Base):
    __tablename__ = 'forecasts'

    forecast_uuid = sa.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    site_uuid = sa.Column(UUID(as_uuid=True), sa.ForeignKey('sites.site_uuid'), nullable=False, default=uuid.uuid4)
    created_utc = sa.Column(TIMESTAMP, nullable=False)
    forecast_version = sa.Column(sa.String(32), nullable=False)

    # one (forecasts) to many (forecast_values)
    forecast_values = relationship("ForecastValueSQL")


class ForecastValueSQL(Base):
    __tablename__ = 'forecast_values'

    forecast_value_uuid = sa.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    datetime_interval_uuid = sa.Column(UUID(as_uuid=True), sa.ForeignKey('datetime_intervals.datetime_interval_uuid'), nullable=False, default=uuid.uuid4)
    forecast_generation_kw = sa.Column(REAL, nullable=False)
    created_utc = sa.Column(TIMESTAMP, nullable=False)
    forecast_uuid = sa.Column(UUID(as_uuid=True), sa.ForeignKey('forecasts.forecast_uuid'), nullable=False, default=uuid.uuid4)


class LatestForecastValueSQL(Base):
    __tablename__ = 'latest_forecast_values'

    latest_forecast_value_uuid = sa.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    datetime_interval_uuid = sa.Column(UUID(as_uuid=True), sa.ForeignKey('datetime_intervals.datetime_interval_uuid'), nullable=False, default=uuid.uuid4)
    forecast_generation_kw = sa.Column(REAL, nullable=False)
    created_utc = sa.Column(TIMESTAMP, nullable=False)
    forecast_uuid = sa.Column(UUID(as_uuid=True), default=uuid.uuid4, nullable=False)
    site_uuid = sa.Column(UUID(as_uuid=True), sa.ForeignKey('sites.site_uuid'), nullable=False, default=uuid.uuid4)
    forecast_version = sa.Column(sa.String(32), nullable=False)

    latest_forecast = relationship("SiteSQL", back_populates="latest_forecast_values")


class ClientSQL(Base):
    __tablename__ = 'clients'

    client_uuid = sa.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    client_name = sa.Column(sa.String(255), nullable=False)
    created_utc = sa.Column(TIMESTAMP, nullable=False)

    sites = relationship("SiteSQL")


class DatetimeIntervalSQL(Base):
    __tablename__ = 'datetime_intervals'

    datetime_interval_uuid = sa.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    start_utc = sa.Column(TIMESTAMP, nullable=False)
    end_utc = sa.Column(TIMESTAMP, nullable=False)
    created_utc = sa.Column(TIMESTAMP, nullable=False)

    generation = relationship("GenerationSQL")
    forecast_values = relationship("ForecastValueSQL")
    latest_forecast_values = relationship("LatestForecastValueSQL")


class StatusSQL(Base):
    __tablename__ = 'status'

    status_uuid = sa.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    status = sa.Column(sa.String(255))
    message = sa.Column(sa.String(255))
    created_utc = sa.Column(TIMESTAMP)
