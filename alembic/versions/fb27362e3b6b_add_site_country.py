"""add_site_country

Revision ID: fb27362e3b6b
Revises: 352bb7f31b06
Create Date: 2024-01-17 14:44:54.464675

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "fb27362e3b6b"
down_revision = "352bb7f31b06"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "sites",
        sa.Column(
            "country",
            sa.String(length=255),
            server_default="uk",
            nullable=True,
            comment="The country in which the site is located",
        ),
    )


def downgrade() -> None:
    """Downgrade"""
    op.drop_column("sites", "country")
