"""Add Inverter table to store inverters linked to sites

Revision ID: 35f53a88b8c3
Revises: aeea08bcfc42
Create Date: 2023-04-20 10:45:07.964865

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "35f53a88b8c3"
down_revision = "aeea08bcfc42"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "inverters",
        sa.Column("created_utc", sa.DateTime(), nullable=True),
        sa.Column("inverter_uuid", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "site_uuid",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            comment="The UUID for the site that has this inverter",
        ),
        sa.Column(
            "client_id",
            sa.String(length=255),
            nullable=True,
            comment="The ID of the inverter as given by the providing client",
        ),
        sa.ForeignKeyConstraint(
            ["site_uuid"],
            ["sites.site_uuid"],
        ),
        sa.PrimaryKeyConstraint("inverter_uuid"),
    )
    op.create_index(op.f("ix_inverters_site_uuid"), "inverters", ["site_uuid"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_inverters_site_uuid"), table_name="inverters")
    op.drop_table("inverters")
