"""site to location

Revision ID: dbd25dac7107
Revises: 81278a3571b2
Create Date: 2025-07-08 12:39:57.105086

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'dbd25dac7107'
down_revision = '81278a3571b2'
branch_labels = None
depends_on = None


location_type = postgresql.ENUM('site', 'region', name='location_type')

def upgrade() -> None:
    location_type.create(op.get_bind())

    op.rename_table("sites", "locations")
    op.rename_table("site_groups", "location_groups")
    op.rename_table("site_group_sites", "location_group_locations")
    op.rename_table("sites_history", "locations_history")

    # add columns
    op.add_column("locations", sa.Column('location_type', sa.Enum('site', 'region', name='location_type'), server_default='site', nullable=False))
    op.add_column('locations', sa.Column('location_metadata', postgresql.JSONB(astext_type=sa.Text()),
                                               server_default=sa.text("'{}'"), nullable=False,
                                               comment='Specific properties of the location, for example for a site, the tilt and orientation of the solar panels, or for a region, the region name.'))
    # rename columns
    op.alter_column('locations', "site_uuid",new_column_name='location_uuid')
    op.alter_column('forecasts', "site_uuid", new_column_name='location_uuid')
    op.alter_column('generation', "site_uuid", new_column_name='location_uuid')
    op.alter_column('inverters', "site_uuid", new_column_name='location_uuid')
    op.alter_column('location_group_locations', "site_uuid", new_column_name='location_uuid')
    op.alter_column('location_group_locations', "site_group_uuid", new_column_name='location_group_uuid')
    op.alter_column('location_group_locations', "site_group_site_uuid", new_column_name='location_group_location_uuid')
    op.alter_column('location_groups', "site_group_uuid", new_column_name='location_group_uuid')
    op.alter_column('location_groups', "site_group_name", new_column_name='location_group_name')
    op.alter_column('locations', "client_site_id", new_column_name='client_location_id')
    op.alter_column('locations', "client_site_name", new_column_name='client_location_name')
    op.alter_column('locations_history', "site_uuid", new_column_name='location_uuid')
    op.alter_column('locations_history', "site_data", new_column_name='location_data')
    op.alter_column('locations_history', "site_history_uuid", new_column_name='location_history_uuid')
    op.alter_column('users', "site_group_uuid", new_column_name='location_group_uuid')

    # rename indexes
    op.execute('ALTER INDEX ix_sites_client_site_id RENAME TO ix_locations_client_location_id')
    op.execute('ALTER INDEX ix_sites_client_site_name RENAME TO ix_locations_client_location_name')
    op.execute('ALTER INDEX ix_sites_client_uuid RENAME TO ix_locations_client_uuid')
    op.execute('ALTER INDEX ix_forecasts_site_uuid_timestamp_utc RENAME TO ix_forecasts_location_uuid_timestamp_utc')
    op.execute('ALTER INDEX ix_generation_site_uuid RENAME TO ix_generation_location_uuid')
    op.execute('ALTER INDEX ix_inverters_site_uuid RENAME TO ix_inverters_location_uuid')
    op.execute('ALTER INDEX ix_site_groups_site_group_name RENAME TO ix_location_groups_location_group_name')
    op.execute('ALTER INDEX ix_sites_history_site_uuid RENAME TO ix_locations_history_location_uuid')

    # rename constraint
    op.execute("ALTER TABLE generation RENAME CONSTRAINT uniq_cons_site_start_end TO uniq_cons_location_start_end")
    op.execute("ALTER TABLE location_group_locations RENAME CONSTRAINT idx_site_group_site TO idx_location_group_location")

    # alter comments in column
    op.alter_column('locations', 'country',
                    comment='The country in which the location is located',)
    op.alter_column('locations', 'capacity_kw',
                    comment='The physical limit on the production capacity of the location')
    op.alter_column('locations', 'ml_id',
                    comment='Auto-incrementing integer ID of the location for use in ML training')
    op.alter_column('locations', 'active',
                    comment='Indicates if location is active')
    op.alter_column('locations', 'client_uuid',
                    comment='The UUID of the client this location belongs to',
                    )
    op.alter_column('locations', 'ml_model_uuid',
                    comment='The ML Model which should be used for this location')
    op.alter_column('locations', 'location_metadata',
                    server_default=None,
                    comment='Specific properties of the location, for example for a location, the tilt and orientation of the solar panels, or for a region, the region name.',)
    op.alter_column('locations', 'region',
                    comment='The region within the country in which the location is located')
    op.alter_column('locations', 'dno',
                    comment='The Distribution Node Operator that owns the location',)
    op.alter_column('locations', 'gsp',
                    comment='The Grid Supply Point in which the location is located',)
    op.alter_column('locations', 'inverter_capacity_kw',
                    comment='The inverter capacity of the location',)
    op.alter_column('locations', 'module_capacity_kw',
                    comment='The PV module nameplate capacity of the location',)
    op.alter_column('forecasts', 'location_uuid',
                    comment='The location for which the forecast sequence was generated',)
    op.alter_column('forecast_values', 'forecast_power_kw',
                    comment='The predicted power generation of this location for the given time interval',)
    op.alter_column('generation', 'generation_power_kw',
                    comment='The actual generated power in kW at this location for this datetime interval',)
    op.alter_column('generation', 'location_uuid',
                    comment='The location for which this generation yield belongs to',
                    )
    op.alter_column('inverters', 'location_uuid',
                    comment='The UUID for the location that has this inverter',
                    )
    op.alter_column('location_group_locations', 'location_group_uuid',
                    comment='The foreign key to the location_groups table',
                    )
    op.alter_column('location_group_locations', 'location_uuid',
                    comment='The foreign key to the locations table',
                    )
    op.alter_column('location_groups', 'service_level',
                    comment='The service level of the location group. 0 is free, 1 is paid.',
                    )
    op.alter_column('locations', 'client_location_id',
                    comment='The ID of the location as given by the providing client',
                    )
    op.alter_column('locations', 'client_location_name',
                    comment='The ID of the location as given by the providing client',
                    )
    op.alter_column('locations_history', 'location_uuid',
                    comment='The location which this history record relates to',
                    )
    op.alter_column('locations_history', 'location_data',
                    comment='A snapshot of the location record as JSONB',
                    )
    op.alter_column('users', 'location_group_uuid',
                    comment='The foreign key to the location_groups table',
                    )

def downgrade() -> None:
    # alter comments in column
    op.alter_column('locations', 'module_capacity_kw',
                    comment='The PV module nameplate capacity of the site',)
    op.alter_column('locations', 'inverter_capacity_kw',
                    comment='The inverter capacity of the site',)
    op.alter_column('locations', 'gsp',
                    comment='The Grid Supply Point in which the site is located',)
    op.alter_column('locations', 'dno',
                    comment='The Distribution Node Operator that owns the site',)
    op.alter_column('locations', 'region',
                    comment='The region within the country in which the site is located',)
    op.alter_column('locations', 'location_metadata',
                    server_default=sa.text("'{}'::jsonb"),
                    comment='Specific properties of the location, for example for a site, the tilt and orientation of the solar panels, or for a region, the region name.',)
    op.alter_column('locations', 'ml_model_uuid',
                    comment='The ML Model which should be used for this site',)
    op.alter_column('locations', 'client_uuid',
                    comment='The UUID of the client this site belongs to',)
    op.alter_column('locations', 'active',
                    comment='Indicates if site is active',)
    op.alter_column('locations', 'ml_id',
                    comment='Auto-incrementing integer ID of the site for use in ML training')
    op.alter_column('locations', 'capacity_kw',
                    comment='The physical limit on the production capacity of the site',
                    )
    op.alter_column('locations', 'country',
                    comment='The country in which the site is located',)
    op.alter_column('forecasts', 'location_uuid',
                    comment='The site for which the forecast sequence was generated',)
    op.alter_column('forecast_values', 'forecast_power_kw',
                    comment='The predicted power generation of this site for the given time interval',)
    op.alter_column('generation', 'generation_power_kw',
                    comment='The actual generated power in kW at this site for this datetime interval',)
    op.alter_column('generation', 'location_uuid',
                    comment='The site for which this generation yield belongs to',
                    )
    op.alter_column('inverters', 'location_uuid',
                    comment='The UUID for the site that has this inverter',
                    )
    op.alter_column('location_group_locations', 'location_group_uuid',
                    comment='The foreign key to the site_groups table',
                    )
    op.alter_column('location_group_locations', 'location_uuid',
                    comment='The foreign key to the sites table',
                    )
    op.alter_column('location_groups', 'service_level',
                    comment='The service level of the site group. 0 is free, 1 is paid.',
                    )
    op.alter_column('locations', 'client_location_id',
                    comment='The ID of the site as given by the providing client',
                    )
    op.alter_column('locations', 'client_location_name',
                    comment='The ID of the site as given by the providing client',
                    )
    op.alter_column('locations_history', 'location_uuid',
                    comment='The site which this history record relates to',
                    )
    op.alter_column('locations_history', 'location_data',
                    comment='A snapshot of the site record as JSONB',
                    )
    op.alter_column('users', 'location_group_uuid',
                    comment='The foreign key to the site_groups table',
                    )

    op.drop_column('locations', 'location_type')
    op.drop_column('locations', 'location_metadata')

    # rename columns
    op.alter_column('locations', "location_uuid", new_column_name='site_uuid')
    op.alter_column('forecasts', "location_uuid", new_column_name='site_uuid')
    op.alter_column('generation', "location_uuid", new_column_name='site_uuid')
    op.alter_column('inverters', "location_uuid", new_column_name='site_uuid')
    op.alter_column('location_group_locations', "location_uuid", new_column_name='site_uuid')
    op.alter_column('location_group_locations', "location_group_uuid", new_column_name='site_group_uuid')
    op.alter_column('location_group_locations', "location_group_location_uuid", new_column_name='site_group_site_uuid')
    op.alter_column('location_groups', "location_group_uuid", new_column_name='site_group_uuid')
    op.alter_column('location_groups', "location_group_name", new_column_name='site_group_name')
    op.alter_column('locations', "client_location_id", new_column_name='client_site_id')
    op.alter_column('locations', "client_location_name", new_column_name='client_site_name')
    op.alter_column('locations_history', "location_uuid", new_column_name='site_uuid')
    op.alter_column('locations_history', "location_data", new_column_name='site_data')
    op.alter_column('locations_history', "location_history_uuid", new_column_name='site_history_uuid')
    op.alter_column('users', "location_group_uuid", new_column_name='site_group_uuid')

    # rename tables
    op.rename_table("locations", "sites")
    op.rename_table("location_groups", "site_groups")
    op.rename_table("location_group_locations", "site_group_sites")
    op.rename_table("locations_history", "sites_history")

    # rename indexes
    op.execute('ALTER INDEX ix_locations_client_location_id RENAME TO ix_sites_client_site_id')
    op.execute('ALTER INDEX ix_locations_client_location_name RENAME TO ix_sites_client_site_name')
    op.execute('ALTER INDEX ix_locations_client_uuid RENAME TO ix_sites_client_uuid')
    op.execute('ALTER INDEX ix_forecasts_location_uuid_timestamp_utc RENAME TO ix_forecasts_site_uuid_timestamp_utc')
    op.execute('ALTER INDEX ix_generation_location_uuid RENAME TO ix_generation_site_uuid')
    op.execute('ALTER INDEX ix_inverters_location_uuid RENAME TO ix_inverters_site_uuid')
    op.execute('ALTER INDEX ix_location_groups_location_group_name RENAME TO ix_site_groups_site_group_name')
    op.execute('ALTER INDEX ix_locations_history_location_uuid RENAME TO ix_sites_history_site_uuid')

    # rename constraint
    op.execute("ALTER TABLE generation RENAME CONSTRAINT uniq_cons_location_start_end TO uniq_cons_site_start_end")
    op.execute(
        "ALTER TABLE site_group_sites RENAME CONSTRAINT idx_location_group_location TO idx_site_group_site")


