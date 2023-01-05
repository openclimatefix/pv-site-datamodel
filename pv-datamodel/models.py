import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID, REAL
from sqlalchemy.schema import UniqueConstraint


Base = declarative_base()


class Pvsite(Base):

    __tablename__ = 'pvsite'

    pvsite_uuid = sa.Column(sa.String(32), sa.ForeignKey('forecast.site_uuid'), primary_key=True)
    client_uuid = sa.Column(sa.String(32), sa.ForeignKey('client.client_uuid'), nullable=False)
    client_site_id = sa.Column(int4())
    client_site_name = sa.Column(sa.String(255))
    region = sa.Column(sa.String(255))
    dno = sa.Column(sa.String(255))
    gsp = sa.Column(sa.String(255))
    orientation = sa.Column(REAL)
    tilt = sa.Column(real())
    latitude = sa.Column(float8(), nullable=False)
    longitude = sa.Column(float8(), nullable=False)
    capacity_kw = sa.Column(REAL, nullable=False)
    created_utc = sa.Column(sa.TIMESTAMP(), nullable=False)
    update_utc = sa.Column(sa.TIMESTAMP(), nullable=False)

    __table_args__ = (
                
    UniqueConstraint("client_site_id",client_uuid, name='idx_client')
            )



class Pvyield(Base):

    __tablename__ = 'pvyield'

    pvyield_uuid = sa.Column(sa.String(32), primary_key=True)
    pvsite_uuid = sa.Column(sa.String(32), sa.ForeignKey('pvsite.pvsite_uuid'), nullable=False)
    generation_kw = sa.Column(real(), nullable=False)
    datetime_interval_uuid = sa.Column(sa.String(32), sa.ForeignKey('datetime_interval.datetime_interval_uuid'), nullable=False)
    created_utc = sa.Column(sa.TIMESTAMP(), nullable=False)


class Forecast(Base):

    __tablename__ = 'forecast'

    forecast_uuid = sa.Column(sa.String(32), primary_key=True)
    site_uuid = sa.Column(sa.String(32), nullable=False)
    created_utc = sa.Column(sa.TIMESTAMP(), nullable=False)
    forecast_version = sa.Column(sa.String(32), nullable=False)


class ForecastValue(Base):

    __tablename__ = 'forecast_value'

    forecast_value_uuid = sa.Column(sa.String(32), primary_key=True)
    datetime_interval_uuid = sa.Column(UUID, sa.ForeignKey('datetime_interval.datetime_interval_uuid'))
    forecast_generation_kw = sa.Column(real())
    created_utc = sa.Column(sa.TIMESTAMP())
    forecast_uuid = sa.Column(sa.String(32), sa.ForeignKey('forecast.forecast_uuid'))


class Client(Base):

    __tablename__ = 'client'

    client_uuid = sa.Column(UUID, primary_key=True)
    client_name = sa.Column(sa.String(32))
    created_utc = sa.Column(sa.TIMESTAMP())


class DatetimeInterval(Base):

    __tablename__ = 'datetime_interval'

    datetime_interval_uuid = sa.Column(UUID, primary_key=True)
    start_utc = sa.Column(sa.TIMESTAMP())
    end_utc = sa.Column(sa.TIMESTAMP())
    created_utc = sa.Column(sa.TIMESTAMP())


class Status(Base):

    __tablename__ = 'status'

    status_uuid = sa.Column(UUID, primary_key=True)
    status = sa.Column(sa.String(32))
    message = sa.Column(sa.String(255))
    created_utc = sa.Column(sa.TIMESTAMP())
