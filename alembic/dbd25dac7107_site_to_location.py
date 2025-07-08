# """site to location
#
# Revision ID: dbd25dac7107
# Revises: 81278a3571b2
# Create Date: 2025-07-08 12:39:57.105086
#
# """
# from alembic import op
# import sqlalchemy as sa
# from sqlalchemy.dialects import postgresql
#
# # revision identifiers, used by Alembic.
# revision = 'dbd25dac7107'
# down_revision = '81278a3571b2'
# branch_labels = None
# depends_on = None
#
#
# def upgrade() -> None:
#     op.rename_table("sites","locations")
#
#
# def downgrade() -> None:
#     op.rename_table("locations", "sites")
