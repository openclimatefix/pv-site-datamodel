"""create trigger

Revision ID: 12c0ccf6b825
Revises: c8ef88c250e7
Create Date: 2024-10-27 20:27:30.805137

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '12c0ccf6b826'
down_revision = 'dbd25dac7107'
branch_labels = None
depends_on = None

def create_trigger(name):
    return f"""CREATE OR REPLACE FUNCTION log_{name}_changes()
RETURNS TRIGGER AS $$
DECLARE
    user_uuid UUID;
BEGIN
    user_uuid := nullif(current_setting('pvsite_datamodel.current_user_uuid', true), '')::UUID;
    
    IF (TG_OP = 'INSERT' OR TG_OP = 'UPDATE') THEN
        INSERT INTO {name}s_history (
            {name}_history_uuid,
            {name}_uuid,
            {name}_data,
            changed_by,
            operation_type,
            created_utc
        ) VALUES (
            gen_random_uuid(),
            NEW.{name}_uuid,
            to_jsonb(NEW),
            user_uuid,
            TG_OP,
            NOW()
        );

    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO {name}s_history (
            {name}_history_uuid,
            {name}_uuid,
            {name}_data,
            changed_by,
            operation_type,
            created_utc
        ) VALUES (
            gen_random_uuid(),
            OLD.{name}_uuid,
            to_jsonb(OLD),
            user_uuid,
            'DELETE',
            NOW()
        );
    END IF;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER {name}_changes_trigger
AFTER INSERT OR UPDATE OR DELETE ON {name}s
FOR EACH ROW EXECUTE FUNCTION log_{name}_changes();
"""

def drop_trigger(name):
    return f"""
DROP TRIGGER IF EXISTS {name}_changes_trigger ON locations;
DROP FUNCTION IF EXISTS log_{name}_changes;
"""

def upgrade() -> None:
    op.execute(create_trigger('location'))
    op.execute(drop_trigger('site'))
    pass


def downgrade() -> None:
    op.execute(drop_trigger('location'))
    op.execute(create_trigger('site'))
    pass
