"""SQLAlchemy definition of the pvsite database schema."""

from __future__ import annotations

# This means we can use Typing of objects that have jet to be defined
import enum
import uuid
from datetime import datetime
from typing import List, Optional

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, declarative_base, relationship
from sqlalchemy.schema import UniqueConstraint

Base = declarative_base()


class CreatedMixin:
    """Mixin to add created datetime to model."""

    created_utc = sa.Column(sa.DateTime, default=lambda: datetime.utcnow())


class MLModelSQL(Base, CreatedMixin):
    """ML model that is being used."""

    __tablename__ = "ml_model"

    model_uuid = sa.Column(UUID, primary_key=True, server_default=sa.func.gen_random_uuid())
    name = sa.Column(sa.String)
    version = sa.Column(sa.String)

    # Add description with default message
    description = sa.Column(sa.String, nullable=True, server_default="No description provided.")

    forecast_values: Mapped[List["ForecastValueSQL"]] = relationship(
        "ForecastValueSQL", back_populates="ml_model"
    )

    locations: Mapped[List["LocationSQL"]] = relationship("LocationSQL", back_populates="ml_model")


class UserSQL(Base, CreatedMixin):
    """Class representing the users table.

    Each user row specifies a single user.
    """

    __tablename__ = "users"
    __tables_args__ = (UniqueConstraint("email", name="idx_email"),)

    user_uuid = sa.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    email = sa.Column(sa.String(255), index=True, unique=True)
    location_group_uuid = sa.Column(
        UUID(as_uuid=True),
        sa.ForeignKey("location_groups.location_group_uuid"),
        nullable=False,
        comment="The foreign key to the location_groups table",
    )

    # Relationships
    location_group: Mapped["LocationGroupSQL"] = relationship(
        "LocationGroupSQL", back_populates="users"
    )
    api_request = relationship("APIRequestSQL", back_populates="user")


class LocationGroupSQL(Base, CreatedMixin):
    """Class representing the location_groups table.

    Each location_group row specifies a single group of locations.
    """

    __tablename__ = "location_groups"

    location_group_uuid = sa.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    location_group_name = sa.Column(sa.String(255), index=True, unique=True)
    service_level = sa.Column(
        sa.Integer,
        default=0,
        comment="The service level of the location group. 0 is free, 1 is paid.",
    )

    # Relationships
    # N-N
    locations: Mapped[List["LocationSQL"]] = relationship(
        "LocationSQL", secondary="location_group_locations", back_populates="location_groups"
    )
    # 1-N, one location group can have many users
    users: Mapped[List[UserSQL]] = relationship("UserSQL", back_populates="location_group")


class LocationGroupLocationSQL(Base, CreatedMixin):
    """Class representing the location_group_locations table.

    Each location_group_location row specifies a single location in a location group.
    """

    __tablename__ = "location_group_locations"
    __table_args__ = (
        UniqueConstraint(
            "location_group_uuid", "location_uuid", name="idx_location_group_location"
        ),
    )

    location_group_location_uuid = sa.Column(
        UUID(as_uuid=True), default=uuid.uuid4, primary_key=True
    )
    location_group_uuid = sa.Column(
        UUID(as_uuid=True),
        sa.ForeignKey("location_groups.location_group_uuid"),
        nullable=False,
        comment="The foreign key to the location_groups table",
    )
    location_uuid = sa.Column(
        UUID(as_uuid=True),
        sa.ForeignKey("locations.location_uuid"),
        nullable=False,
        comment="The foreign key to the locations table",
    )


class LocationLocationSQL(Base, CreatedMixin):
    """Class representing the location_locations table.

    Each location_to_location row specifies a single location in a location.
    We want to to be able to attaches multiple sites to several regions.
    E.g. pv solar sites in a GSP region, and a National Grid region.
    """

    __tablename__ = "location_locations"
    __table_args__ = (
        UniqueConstraint(
            "location_child_uuid", "location_parent_uuid", name="idx_location_location"
        ),
    )

    location_location_uuid = sa.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    location_parent_uuid = sa.Column(
        UUID(as_uuid=True),
        sa.ForeignKey("locations.location_uuid"),
        nullable=False,
        comment="The foreign key to the locations table",
    )
    location_child_uuid = sa.Column(
        UUID(as_uuid=True),
        sa.ForeignKey("locations.location_uuid"),
        nullable=False,
        comment="The foreign key to the locations table",
    )


class LocationAssetType(enum.Enum):
    """Enum type representing a location's asset type."""

    pv = 1
    wind = 2


class LocationType(enum.Enum):
    """Enum type representing a location's location type."""

    site = 1
    region = 2


class LocationSQL(Base, CreatedMixin):
    """Class representing the locations table.

    Each location row specifies location in space. It can represent
    - a solar single panel
    - cluster of solar panels found on a residential house or commercial building.
    - a large solar farm
    - a wind farm

    # TODO update this to LocationSQL in future release + other renames
    """

    __tablename__ = "locations"

    location_uuid = sa.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    client_location_id = sa.Column(
        sa.Integer, index=True, comment="The ID of the location as given by the providing client"
    )
    client_location_name = sa.Column(
        sa.String(255),
        index=True,
        comment="The ID of the location as given by the providing client",
    )

    country = sa.Column(
        sa.String(255), server_default="uk", comment="The country in which the location is located"
    )

    asset_type = sa.Column(
        sa.Enum(LocationAssetType, name="site_asset_type"),
        nullable=False,
        server_default=LocationAssetType.pv.name,
    )

    latitude = sa.Column(sa.Float)
    longitude = sa.Column(sa.Float)
    capacity_kw = sa.Column(
        sa.Float, comment="The physical limit on the production capacity of the location"
    )

    ml_id = sa.Column(
        sa.Integer,
        autoincrement=True,
        nullable=False,
        comment="Auto-incrementing integer ID of the location for use in ML training",
    )

    active = sa.Column(
        sa.Boolean,
        default=True,
        unique=False,
        comment="Indicates if location is active",
    )

    client_uuid = sa.Column(
        UUID(as_uuid=True),
        sa.ForeignKey("clients.client_uuid"),
        nullable=True,
        index=True,
        comment="The UUID of the client this location belongs to",
    )

    ml_model_uuid = sa.Column(
        UUID(as_uuid=True),
        sa.ForeignKey("ml_model.model_uuid"),
        nullable=True,
        comment="The ML Model which should be used for this location",
    )
    # new fields
    location_type = sa.Column(
        sa.Enum(LocationType, name="location_type"),
        nullable=False,
        server_default=LocationType.site.name,
    )
    location_metadata = sa.Column(
        JSONB,
        nullable=True,
        comment="Specific properties of the location, "
        "for example for a location, the tilt and orientation of the "
        "solar panels, or for a region, the region name.",
    )

    # legacy fields
    region = sa.Column(
        sa.String(255), comment="The region within the country in which the location is located"
    )
    dno = sa.Column(sa.String(255), comment="The Distribution Node Operator that owns the location")
    gsp = sa.Column(
        sa.String(255), comment="The Grid Supply Point in which the location is located"
    )
    # For metadata `NULL` means "we don't know".
    orientation = sa.Column(
        sa.Float, comment="The rotation of the panel in degrees. 180° points south"
    )
    tilt = sa.Column(
        sa.Float, comment="The tile of the panel in degrees. 90° indicates the panel is vertical"
    )
    inverter_capacity_kw = sa.Column(sa.Float, comment="The inverter capacity of the location")
    module_capacity_kw = sa.Column(
        sa.Float, comment="The PV module nameplate capacity of the location"
    )

    # relationships
    forecasts: Mapped[List["ForecastSQL"]] = relationship("ForecastSQL", back_populates="location")
    generation: Mapped[List["GenerationSQL"]] = relationship("GenerationSQL")
    inverters: Mapped[List["InverterSQL"]] = relationship(
        "InverterSQL", back_populates="location", cascade="all, delete-orphan"
    )
    location_groups: Mapped[List["LocationGroupSQL"]] = relationship(
        "LocationGroupSQL", secondary="location_group_locations", back_populates="locations"
    )
    client: Mapped[List["ClientSQL"]] = relationship("ClientSQL", back_populates="locations")
    ml_model: Mapped[Optional[MLModelSQL]] = relationship("MLModelSQL", back_populates="locations")

    # n:n mapping to reference back to locations.
    # This means many site can be part of a many different regions.
    child_locations: Mapped[List["LocationSQL"]] = relationship(
        "LocationSQL",
        secondary="location_locations",
        primaryjoin="LocationSQL.location_uuid == LocationLocationSQL.location_child_uuid",
        secondaryjoin="LocationSQL.location_uuid == LocationLocationSQL.location_parent_uuid",
        backref="parent_locations",
    )


class LocationHistorySQL(Base, CreatedMixin):
    """Class representing the locations history table.

    Stores a history of changes to locatios over time. Uses JSONB so that schema changes to the
    location table do not affect the history table.
    """

    __tablename__ = "locations_history"

    location_history_uuid = sa.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)

    location_uuid = sa.Column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="The location which this history record relates to",
    )

    # JSONB column to store the snapshot of the location data
    location_data = sa.Column(
        JSONB, nullable=False, comment="A snapshot of the location record as JSONB"
    )

    # Foreign key to track the user who made the change
    changed_by = sa.Column(UUID(as_uuid=True), sa.ForeignKey("users.user_uuid"), nullable=True)

    operation_type = sa.Column(sa.TEXT, nullable=False)


class ClientSQL(Base, CreatedMixin):
    """Class representing the client table.

    Each client row specifies a single client.
    """

    __tablename__ = "clients"

    client_uuid = sa.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    client_name = sa.Column(sa.String(255), nullable=False, index=True, unique=True)

    locations: Mapped[List[LocationSQL]] = relationship("LocationSQL", back_populates="client")


class GenerationSQL(Base, CreatedMixin):
    """Class representing the generation table.

    Each generation row specifies a generated power output over a
    given time range for a location.

    *Approximate size: *
    Generation populated every 5 minutes per location * 4000 locations = ~1,125,000 rows per day
    """

    __tablename__ = "generation"
    __table_args__ = (
        UniqueConstraint(
            "location_uuid", "start_utc", "end_utc", name="uniq_cons_location_start_end"
        ),
    )

    generation_uuid = sa.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    location_uuid = sa.Column(
        UUID(as_uuid=True),
        sa.ForeignKey("locations.location_uuid"),
        nullable=False,
        index=True,
        comment="The location for which this generation yield belongs to",
    )
    generation_power_kw = sa.Column(
        sa.Float,
        nullable=False,
        comment="The actual generated power in kW at this location for this datetime interval",
    )

    start_utc = sa.Column(
        sa.DateTime,
        nullable=False,
        index=True,
        comment="The start of the time interval over which this generated power value applies",
    )
    end_utc = sa.Column(
        sa.DateTime,
        nullable=False,
        comment="The end of the time interval over which this generated power value applies",
    )

    location: Mapped["LocationSQL"] = relationship("LocationSQL", back_populates="generation")


class ForecastSQL(Base, CreatedMixin):
    """Class representing the forecasts table.

    Each forecast row refers to a sequence of predicted solar generation values
    over a set of target times for one location.

    *Approximate size: *
    One forecast per location every 5 minutes = ~1,125,000 rows per day
    """

    __tablename__ = "forecasts"

    forecast_uuid = sa.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    location_uuid = sa.Column(
        UUID(as_uuid=True),
        sa.ForeignKey("locations.location_uuid"),
        nullable=False,
        comment="The location for which the forecast sequence was generated",
    )

    # The timestamp at which we are making the forecast. This is often referred as "now" in the
    # modelling code.
    # Note that this could be very different from the `created_utc` time, for instance if we
    # run the model for a given "now" timestamp in the past.
    timestamp_utc = sa.Column(
        sa.DateTime,
        nullable=False,
        comment="The creation time of the forecast sequence",
    )

    forecast_version = sa.Column(
        sa.String(32),
        nullable=False,
        comment="The semantic version of the model used to generate the forecast",
    )

    # one (forecasts) to many (forecast_values)
    forecast_values: Mapped["ForecastValueSQL"] = relationship("ForecastValueSQL")
    location = relationship("LocationSQL", back_populates="forecasts")

    __table_args__ = (
        # With this index, we are assuming that it doesn't make sense to do a query solely on
        # `timestamp_utc`: we always also filter by location_uuid.
        sa.Index("ix_forecasts_location_uuid_timestamp_utc", "location_uuid", "timestamp_utc"),
    )


class ForecastValueSQL(Base, CreatedMixin):
    """Class representing the forecast_values table.

    Each forecast_value row is a prediction for the power output
    of a location over a target datetime interval. Many predictions
    are made for each location at each target interval.

    *Approximate size: *
    One forecast value every 5 minutes per location per forecast.
    Each forecast's prediction sequence covers 24 hours of target
    intervals = ~324,000,000 rows per day
    """

    __tablename__ = "forecast_values"

    forecast_value_uuid = sa.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)

    start_utc = sa.Column(
        sa.DateTime,
        nullable=False,
        index=True,
        comment="The start of the time interval over which this predicted power value applies",
    )
    end_utc = sa.Column(
        sa.DateTime,
        nullable=False,
        comment="The end of the time interval over which this predicted power value applies",
    )
    forecast_power_kw = sa.Column(
        sa.Float,
        nullable=False,
        comment="The predicted power generation of this location for the given time interval",
    )

    # This is the different between `start_utc` and the `forecast`'s `timestamp_utc`, in minutes.
    # It's useful to have it in its own column to efficiently query forecasts for a given horizon.
    horizon_minutes = sa.Column(
        sa.Integer,
        nullable=False,
        server_default=sa.text("-1"),
        comment=(
            "The time difference between the creation time of the forecast value "
            "and the start of the time interval it applies for"
        ),
    )

    forecast_uuid = sa.Column(
        UUID(as_uuid=True),
        sa.ForeignKey("forecasts.forecast_uuid"),
        nullable=False,
        comment="The forecast sequence this forcast value belongs to",
    )
    ml_model_uuid = sa.Column(
        UUID(as_uuid=True),
        sa.ForeignKey("ml_model.model_uuid"),
        nullable=True,
        comment="The ML Model this forcast value belongs to",
    )

    probabilistic_values = sa.Column(
        JSONB,
        nullable=False,
        server_default=sa.text("'{}'"),  # Default to an empty JSON object
        comment="Probabilistic forecast values, like p10, p50, p90",
    )

    forecast: Mapped["ForecastSQL"] = relationship("ForecastSQL", back_populates="forecast_values")
    ml_model: Mapped[Optional[MLModelSQL]] = relationship(
        "MLModelSQL", back_populates="forecast_values"
    )

    __table_args__ = (
        # Here we assume that we always filter on `horizon_minutes` *for given forecasts*.
        sa.Index(
            "ix_forecast_values_forecast_uuid_horizon_minutes", "forecast_uuid", "horizon_minutes"
        ),
    )


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


class InverterSQL(Base, CreatedMixin):
    """Class representing the inverters table.

    Each InverterSQL row represents an inverter tied to a LocationSQL row.

    *Approximate size: *
    4 clients * ~1000 locations each * ~1 inverter each = ~4000 rows
    """

    __tablename__ = "inverters"

    inverter_uuid = sa.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    location_uuid = sa.Column(
        UUID(as_uuid=True),
        sa.ForeignKey("locations.location_uuid"),
        nullable=False,
        index=True,
        comment="The UUID for the location that has this inverter",
    )

    location: Mapped["LocationSQL"] = relationship("LocationSQL", back_populates="inverters")


class APIRequestSQL(Base, CreatedMixin):
    """Information about what API route was called."""

    __tablename__ = "api_request"

    uuid = sa.Column(UUID, primary_key=True, server_default=sa.func.gen_random_uuid())
    url = sa.Column(sa.String)

    user_uuid = sa.Column(UUID, sa.ForeignKey("users.user_uuid"), index=True)
    user = relationship("UserSQL", back_populates="api_request")
