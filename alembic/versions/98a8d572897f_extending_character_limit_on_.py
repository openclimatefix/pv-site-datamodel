"""Extending character limit on ForecastSQL.forecast_version field

Revision ID: 98a8d572897f
Revises: fb27362e3b6b
Create Date: 2024-02-29 13:07:16.473914

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '98a8d572897f'
down_revision = 'fb27362e3b6b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column('forecasts', 'forecast_version',
               existing_type=sa.VARCHAR(length=32),
               type_=sa.String(length=40),
               comment='The version of the model used to generate the forecast (semantic or commit hash)',
               existing_nullable=False)


def downgrade() -> None:
    op.alter_column('forecasts', 'forecast_version',
               existing_type=sa.String(length=40),
               type_=sa.VARCHAR(length=32),
               comment='The semantic version of the model used to generate the forecast',
               existing_nullable=False)

