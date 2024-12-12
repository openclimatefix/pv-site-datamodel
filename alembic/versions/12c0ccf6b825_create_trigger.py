"""create trigger

Revision ID: 12c0ccf6b825
Revises: c8ef88c250e7
Create Date: 2024-10-27 20:27:30.805137

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '12c0ccf6b825'
down_revision = 'c8ef88c250e7'
branch_labels = None
depends_on = None

create_trigger = """CREATE OR REPLACE FUNCTION log_site_changes()
RETURNS TRIGGER AS $$
DECLARE
    user_uuid UUID;
BEGIN
    user_uuid := nullif(current_setting('pvsite_datamodel.current_user_uuid', true), '')::UUID;
    
    IF (TG_OP = 'INSERT' OR TG_OP = 'UPDATE') THEN
        INSERT INTO sites_history (
            site_history_uuid,
            site_uuid,
            site_data,
            changed_by,
            operation_type,
            created_utc
        ) VALUES (
            gen_random_uuid(),
            NEW.site_uuid,
            to_jsonb(NEW),
            user_uuid,
            TG_OP,
            NOW()
        );

    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO sites_history (
            site_history_uuid,
            site_uuid,
            site_data,
            changed_by,
            operation_type,
            created_utc
        ) VALUES (
            gen_random_uuid(),
            OLD.site_uuid,
            to_jsonb(OLD),
            user_uuid,
            'DELETE',
            NOW()
        );
    END IF;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER site_changes_trigger
AFTER INSERT OR UPDATE OR DELETE ON sites
FOR EACH ROW EXECUTE FUNCTION log_site_changes();
"""

drop_trigger = """
DROP TRIGGER IF EXISTS site_changes_trigger ON sites;
DROP FUNCTION IF EXISTS log_site_changes;
"""

def upgrade() -> None:
    op.execute(create_trigger)
    pass


def downgrade() -> None:
    op.execute(drop_trigger)
    pass
