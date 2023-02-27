"""Add timestamp_utc column to forecasts table

Revision ID: 830bec1172a8
Revises: 4e1eb8b4e7f2
Create Date: 2023-02-23 22:15:18.563516

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "830bec1172a8"
down_revision = "4e1eb8b4e7f2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop the site_uuid column in the forecast_values table.
    #
    op.drop_index("ix_forecast_values_site_uuid", table_name="forecast_values")
    op.drop_constraint("forecast_values_site_uuid_fkey", "forecast_values", type_="foreignkey")
    op.drop_column("forecast_values", "site_uuid")

    # Add a `timestamp_utc` column in the `forecasts` table.
    #
    # First we temporary allow NULL.
    op.add_column("forecasts", sa.Column("timestamp_utc", sa.DateTime(), nullable=True))
    # For historical data, use the value of `created_utc`. This should be close enough.
    op.execute("UPDATE forecasts SET timestamp_utc=created_utc")
    # Then we can properly set it as NOT NULL
    op.alter_column("forecasts", "timestamp_utc", nullable=False)
    # Add an index on the new column.
    op.create_index(
        op.f("ix_forecasts_timestamp_utc"), "forecasts", ["timestamp_utc"], unique=False
    )
