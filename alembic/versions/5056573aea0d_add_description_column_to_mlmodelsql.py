"""Add description column to MLModelSQL

Revision ID: 5056573aea0d
Revises: d5c9e13a8b66
Create Date: 2024-11-30 12:41:40.018225

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '5056573aea0d'
down_revision = 'd5c9e13a8b66'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('forecast_values', 'start_utc',
               existing_type=postgresql.TIMESTAMP(),
               comment='The start of the time interval over which this predicted power value applies',
               existing_nullable=False)
    op.alter_column('forecast_values', 'end_utc',
               existing_type=postgresql.TIMESTAMP(),
               comment='The end of the time interval over which this predicted power value applies',
               existing_nullable=False)
    op.alter_column('forecast_values', 'forecast_power_kw',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               comment='The predicted power generation of this site for the given time interval',
               existing_nullable=False)
    op.alter_column('forecast_values', 'horizon_minutes',
               existing_type=sa.INTEGER(),
               comment='The time difference between the creation time of the forecast value and the start of the time interval it applies for',
               existing_nullable=True)
    op.alter_column('forecast_values', 'forecast_uuid',
               existing_type=sa.UUID(),
               comment='The forecast sequence this forcast value belongs to',
               existing_nullable=False)
    op.alter_column('forecasts', 'site_uuid',
               existing_type=sa.UUID(),
               comment='The site for which the forecast sequence was generated',
               existing_nullable=False)
    op.alter_column('forecasts', 'timestamp_utc',
               existing_type=postgresql.TIMESTAMP(),
               comment='The creation time of the forecast sequence',
               existing_nullable=False)
    op.alter_column('forecasts', 'forecast_version',
               existing_type=sa.VARCHAR(length=32),
               comment='The semantic version of the model used to generate the forecast',
               existing_nullable=False)
    op.alter_column('generation', 'site_uuid',
               existing_type=sa.UUID(),
               comment='The site for which this geenration yield belongs to',
               existing_nullable=False)
    op.alter_column('generation', 'generation_power_kw',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               comment='The actual generated power in kW at this site for this datetime interval',
               existing_nullable=False)
    op.alter_column('generation', 'start_utc',
               existing_type=postgresql.TIMESTAMP(),
               comment='The start of the time interval over which this generated power value applies',
               existing_nullable=False)
    op.alter_column('generation', 'end_utc',
               existing_type=postgresql.TIMESTAMP(),
               comment='The end of the time interval over which this generated power value applies',
               existing_nullable=False)
    op.add_column('ml_model', sa.Column('description', sa.String(), nullable=True))
    op.alter_column('site_groups', 'service_level',
               existing_type=sa.INTEGER(),
               comment='The service level of the site group. 0 is free, 1 is paid.',
               existing_comment='The service level of the site group. 0 is free1 is paid',
               existing_nullable=True)
    op.alter_column('sites', 'client_site_id',
               existing_type=sa.INTEGER(),
               comment='The ID of the site as given by the providing client',
               existing_nullable=True)
    op.alter_column('sites', 'client_site_name',
               existing_type=sa.VARCHAR(length=255),
               comment='The ID of the site as given by the providing client',
               existing_nullable=True)
    op.alter_column('sites', 'region',
               existing_type=sa.VARCHAR(length=255),
               comment='The region within the country in which the site is located',
               existing_nullable=True)
    op.alter_column('sites', 'dno',
               existing_type=sa.VARCHAR(length=255),
               comment='The Distribution Node Operator that owns the site',
               existing_nullable=True)
    op.alter_column('sites', 'gsp',
               existing_type=sa.VARCHAR(length=255),
               comment='The Grid Supply Point in which the site is located',
               existing_nullable=True)
    op.alter_column('sites', 'orientation',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               comment='The rotation of the panel in degrees. 180° points south',
               existing_nullable=True)
    op.alter_column('sites', 'tilt',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               comment='The tile of the panel in degrees. 90° indicates the panel is vertical',
               existing_nullable=True)
    op.alter_column('sites', 'capacity_kw',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               comment='The physical limit on the production capacity of the site',
               existing_nullable=True)
    op.alter_column('sites', 'inverter_capacity_kw',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               comment='The inverter capacity of the site',
               existing_comment='The PV module nameplate capacity of the site',
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('sites', 'inverter_capacity_kw',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               comment='The PV module nameplate capacity of the site',
               existing_comment='The inverter capacity of the site',
               existing_nullable=True)
    op.alter_column('sites', 'capacity_kw',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               comment=None,
               existing_comment='The physical limit on the production capacity of the site',
               existing_nullable=True)
    op.alter_column('sites', 'tilt',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               comment=None,
               existing_comment='The tile of the panel in degrees. 90° indicates the panel is vertical',
               existing_nullable=True)
    op.alter_column('sites', 'orientation',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               comment=None,
               existing_comment='The rotation of the panel in degrees. 180° points south',
               existing_nullable=True)
    op.alter_column('sites', 'gsp',
               existing_type=sa.VARCHAR(length=255),
               comment=None,
               existing_comment='The Grid Supply Point in which the site is located',
               existing_nullable=True)
    op.alter_column('sites', 'dno',
               existing_type=sa.VARCHAR(length=255),
               comment=None,
               existing_comment='The Distribution Node Operator that owns the site',
               existing_nullable=True)
    op.alter_column('sites', 'region',
               existing_type=sa.VARCHAR(length=255),
               comment=None,
               existing_comment='The region within the country in which the site is located',
               existing_nullable=True)
    op.alter_column('sites', 'client_site_name',
               existing_type=sa.VARCHAR(length=255),
               comment=None,
               existing_comment='The ID of the site as given by the providing client',
               existing_nullable=True)
    op.alter_column('sites', 'client_site_id',
               existing_type=sa.INTEGER(),
               comment=None,
               existing_comment='The ID of the site as given by the providing client',
               existing_nullable=True)
    op.alter_column('site_groups', 'service_level',
               existing_type=sa.INTEGER(),
               comment='The service level of the site group. 0 is free1 is paid',
               existing_comment='The service level of the site group. 0 is free, 1 is paid.',
               existing_nullable=True)
    op.drop_column('ml_model', 'description')
    op.alter_column('generation', 'end_utc',
               existing_type=postgresql.TIMESTAMP(),
               comment=None,
               existing_comment='The end of the time interval over which this generated power value applies',
               existing_nullable=False)
    op.alter_column('generation', 'start_utc',
               existing_type=postgresql.TIMESTAMP(),
               comment=None,
               existing_comment='The start of the time interval over which this generated power value applies',
               existing_nullable=False)
    op.alter_column('generation', 'generation_power_kw',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               comment=None,
               existing_comment='The actual generated power in kW at this site for this datetime interval',
               existing_nullable=False)
    op.alter_column('generation', 'site_uuid',
               existing_type=sa.UUID(),
               comment=None,
               existing_comment='The site for which this geenration yield belongs to',
               existing_nullable=False)
    op.alter_column('forecasts', 'forecast_version',
               existing_type=sa.VARCHAR(length=32),
               comment=None,
               existing_comment='The semantic version of the model used to generate the forecast',
               existing_nullable=False)
    op.alter_column('forecasts', 'timestamp_utc',
               existing_type=postgresql.TIMESTAMP(),
               comment=None,
               existing_comment='The creation time of the forecast sequence',
               existing_nullable=False)
    op.alter_column('forecasts', 'site_uuid',
               existing_type=sa.UUID(),
               comment=None,
               existing_comment='The site for which the forecast sequence was generated',
               existing_nullable=False)
    op.alter_column('forecast_values', 'forecast_uuid',
               existing_type=sa.UUID(),
               comment=None,
               existing_comment='The forecast sequence this forcast value belongs to',
               existing_nullable=False)
    op.alter_column('forecast_values', 'horizon_minutes',
               existing_type=sa.INTEGER(),
               comment=None,
               existing_comment='The time difference between the creation time of the forecast value and the start of the time interval it applies for',
               existing_nullable=True)
    op.alter_column('forecast_values', 'forecast_power_kw',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               comment=None,
               existing_comment='The predicted power generation of this site for the given time interval',
               existing_nullable=False)
    op.alter_column('forecast_values', 'end_utc',
               existing_type=postgresql.TIMESTAMP(),
               comment=None,
               existing_comment='The end of the time interval over which this predicted power value applies',
               existing_nullable=False)
    op.alter_column('forecast_values', 'start_utc',
               existing_type=postgresql.TIMESTAMP(),
               comment=None,
               existing_comment='The start of the time interval over which this predicted power value applies',
               existing_nullable=False)
    # ### end Alembic commands ###