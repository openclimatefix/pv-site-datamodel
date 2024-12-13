"""site history table

Revision ID: c8ef88c250e7
Revises: 7a32241916f7
Create Date: 2024-11-29 22:42:25.535162

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'c8ef88c250e7'
down_revision = '7a32241916f7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('sites_history',
    sa.Column('site_history_uuid', sa.UUID(), nullable=False),
    sa.Column('site_uuid', sa.UUID(), nullable=False, comment='The site which this history record relates to'),
    sa.Column('site_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False, comment='A snapshot of the site record as JSONB'),
    sa.Column('changed_by', sa.UUID(), nullable=True),
    sa.Column('operation_type', sa.TEXT(), nullable=False),
    sa.Column('created_utc', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['changed_by'], ['users.user_uuid'], ),
    sa.PrimaryKeyConstraint('site_history_uuid')
    )
    op.create_index(op.f('ix_sites_history_site_uuid'), 'sites_history', ['site_uuid'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_sites_history_site_uuid'), table_name='sites_history')
    op.drop_table('sites_history')
