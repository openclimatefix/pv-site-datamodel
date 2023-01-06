import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.schema import UniqueConstraint


Base = declarative_base()


class Sites(Base):

    __tablename__ = 'sites'

    site_uuid = sa.Column(UUID, sa.ForeignKey('forecasts.site_uuid'), sa.ForeignKey('latest_forecast_values.site_uuid'), primary_key=True)
    client_uuid = sa.Column(UUID, sa.ForeignKey('clients.client_uuid'), nullable=False)
    client_site_id = sa.Column(int4())
    client_site_name = sa.Column(sa.String(255))
    region = sa.Column(sa.String(255))
    dno = sa.Column(sa.String(255))
    gsp = sa.Column(sa.String(255))
    orientation = sa.Column(real())
    tilt = sa.Column(real())
    latitude = sa.Column(float8(), nullable=False)
    longitude = sa.Column(float8(), nullable=False)
    capacity_kw = sa.Column(real(), nullable=False)
    created_utc = sa.Column(sa.TIMESTAMP(), nullable=False)
    updated_utc = sa.Column(sa.TIMESTAMP(), nullable=False)

    __table_args__ = (
                
    UniqueConstraint("client_site_id",client_uuid, name='idx_client')
            )



class Generation(Base):

    __tablename__ = 'generation'

    generation_uuid = sa.Column(UUID, primary_key=True)
    site_uuid = sa.Column(UUID, sa.ForeignKey('sites.site_uuid'), nullable=False)
    power_kw = sa.Column(real(), nullable=False)
    datetime_interval_uuid = sa.Column(UUID, sa.ForeignKey('datetime_intervals.datetime_interval_uuid'), nullable=False)
    created_utc = sa.Column(sa.TIMESTAMP(), nullable=False)


class Forecasts(Base):

    __tablename__ = 'forecasts'

    forecast_uuid = sa.Column(UUID, primary_key=True)
    site_uuid = sa.Column(UUID, nullable=False)
    created_utc = sa.Column(sa.TIMESTAMP(), nullable=False)
    forecast_version = sa.Column(sa.String(32), nullable=False)


class ForecastValues(Base):

    __tablename__ = 'forecast_values'

    forecast_value_uuid = sa.Column(UUID, primary_key=True)
    datetime_interval_uuid = sa.Column(UUID, sa.ForeignKey('datetime_intervals.datetime_interval_uuid'), nullable=False)
    forecast_generation_kw = sa.Column(real(), nullable=False)
    created_utc = sa.Column(sa.TIMESTAMP(), nullable=False)
    forecast_uuid = sa.Column(UUID, sa.ForeignKey('forecasts.forecast_uuid'), nullable=False)


class LatestForecastValues(Base):

    __tablename__ = 'latest_forecast_values'

    latest_forecast_value_uuid = sa.Column(UUID, primary_key=True)
    datetime_interval_uuid = sa.Column(UUID, sa.ForeignKey('datetime_intervals.datetime_interval_uuid'), nullable=False)
    forecast_generation_kw = sa.Column(real(), nullable=False)
    created_utc = sa.Column(sa.TIMESTAMP(), nullable=False)
    forecast_uuid = sa.Column(UUID, nullable=False)
    site_uuid = sa.Column(UUID, nullable=False)
    forecast_version = sa.Column(sa.String(32), nullable=False)


class Clients(Base):

    __tablename__ = 'clients'

    client_uuid = sa.Column(UUID, primary_key=True)
    client_name = sa.Column(sa.String(255), nullable=False)
    created_utc = sa.Column(sa.TIMESTAMP(), nullable=False)


class DatetimeIntervals(Base):

    __tablename__ = 'datetime_intervals'

    datetime_interval_uuid = sa.Column(UUID, primary_key=True)
    start_utc = sa.Column(sa.TIMESTAMP(), nullable=False)
    end_utc = sa.Column(sa.TIMESTAMP(), nullable=False)
    created_utc = sa.Column(sa.TIMESTAMP(), nullable=False)


class Status(Base):

    __tablename__ = 'status'

    status_uuid = sa.Column(UUID, primary_key=True)
    status = sa.Column(sa.String(255))
    message = sa.Column(sa.String(255))
    created_utc = sa.Column(sa.TIMESTAMP())
