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
    op.add_column("locations", sa.Column('location_type', sa.Enum('site', 'region', name='location_type'), server_default='site', nullable=False))
    op.add_column('locations', sa.Column('location_metadata', postgresql.JSONB(astext_type=sa.Text()),
                                               server_default=sa.text("'{}'"), nullable=False,
                                               comment='Specific properties of the location'))



def downgrade() -> None:
    op.drop_column('locations', 'location_type')
    op.drop_column('locations', 'location_metadata')
    op.rename_table("locations", "sites")

