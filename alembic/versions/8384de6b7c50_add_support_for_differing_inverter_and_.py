"""Add support for differing inverter and module capacities

Revision ID: 8384de6b7c50
Revises: 35f53a88b8c3
Create Date: 2023-04-08 12:26:23.042938

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "8384de6b7c50"
down_revision = "35f53a88b8c3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "sites",
        sa.Column(
            "module_capacity_kw",
            sa.Float(),
            nullable=True,
            comment="The PV module nameplate capacity of the site",
        ),
    )
    op.add_column(
        "sites",
        sa.Column(
            "inverter_capacity_kw",
            sa.Float(),
            nullable=True,
            comment="The PV module nameplate capacity of the site",
        ),
    )

    op.execute("UPDATE sites SET inverter_capacity_kw=capacity_kw")

    # Create a trigger function to set inverter_capacity_kw to capacity_kw
    op.execute(
        """
        CREATE OR REPLACE FUNCTION set_default_inverter_capacity_kw()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.inverter_capacity_kw := NEW.capacity_kw;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """
    )

    # Create trigger on sites table, for when inverter_capacity_kw is NULL
    op.execute(
        """
        CREATE TRIGGER set_default_inverter_capacity_kw_trigger
        BEFORE INSERT ON sites
        FOR EACH ROW
        WHEN (NEW.inverter_capacity_kw IS NULL)
        EXECUTE FUNCTION set_default_inverter_capacity_kw();
    """
    )


def downgrade() -> None:
    # Drop the trigger from the 'sites' table
    op.execute(
        """
        DROP TRIGGER set_default_inverter_capacity_kw_trigger ON sites;
    """
    )

    # Drop the trigger function
    op.execute(
        """
        DROP FUNCTION set_default_inverter_capacity_kw;
    """
    )

    op.drop_column("sites", "module_capacity_kw")
    op.drop_column("sites", "inverter_capacity_kw")
