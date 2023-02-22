""" App for running database migrations """
import logging
import os
import time

import click
from alembic import command
from alembic.config import Config

filename = os.path.dirname(os.path.abspath(__file__)) + "/alembic.ini"

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("LOGLEVEL", "INFO"))


@click.command()
@click.option(
    "--make-migrations",
    default=False,
    envvar="MAKE_MIGRATIONS",
    help="Option to make database migrations",
    type=click.BOOL,
    is_flag=True,
)
@click.option(
    "--run-migrations",
    default=False,
    envvar="RUN_MIGRATIONS",
    help="Option to run the database migrations",
    type=click.BOOL,
    is_flag=True,
)
def app(make_migrations: bool, run_migrations: bool):
    """
    Make migrations and run them

    :param make_migrations: option to make the database migrations
    :param run_migrations: option to run migrations
    """

    # some times need 1 second for the database to get started
    time.sleep(1)

    if make_migrations:
        make_all_migrations()

    if run_migrations:
        run_all_migrations()


def make_all_migrations():
    """
    Make migrations.

    They are saved in
    nowcasting_datamodel/alembic/{database}/version
    """

    logger.info(f"Making migrations")

    alembic_cfg = Config(filename, ini_section='db')
    command.revision(alembic_cfg, autogenerate=True)

    logger.info("Making migrations:done")


def run_all_migrations():
    """Run migrations

    Looks at the migrations in
    nowcasting_datamodel/alembic/{database}/version
    and runs them
    """

    logger.info(f"Running migrations")

    # see here - https://alembic.sqlalchemy.org/en/latest/api/config.html
    # for more help
    alembic_cfg = Config(filename, ini_section='db')

    command.upgrade(alembic_cfg, "head")

    logger.info(f"Running migrations: done")


if __name__ == "__main__":
    app()
