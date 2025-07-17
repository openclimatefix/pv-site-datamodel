import os
import subprocess

from testcontainers.postgres import PostgresContainer


def test_migrations():
    """Run the alembic migrations on a clean database."""
    with PostgresContainer("postgres:14.5") as postgres:
        url = postgres.get_connection_url()

        env = os.environ.copy()
        env["DB_URL"] = url
        result = subprocess.run(["alembic", "upgrade", "head"], env=env) # noqa: S607
        assert result.returncode == 0
