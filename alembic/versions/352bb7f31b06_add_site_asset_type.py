"""add_site_asset_type

Revision ID: 352bb7f31b06
Revises: d60cb99ff9e6
Create Date: 2024-01-10 11:58:02.448702

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '352bb7f31b06'
down_revision = 'd60cb99ff9e6'
branch_labels = None
depends_on = None

site_asset_type = postgresql.ENUM('pv', 'wind', name='site_asset_type')

def upgrade() -> None:
    site_asset_type.create(op.get_bind())
    op.add_column('sites', sa.Column('asset_type', sa.Enum('pv', 'wind', name='site_asset_type'), server_default='pv', nullable=False))

def downgrade() -> None:
    op.drop_column('sites', 'asset_type')
    site_asset_type.drop(op.get_bind())
