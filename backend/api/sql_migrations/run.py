import os

from alembic.command import upgrade
from alembic.config import Config
from sqlalchemy.ext.asyncio import create_async_engine
from structlog import get_logger

from backend.api.sql_migrations.insert_scripts import caller


def run_upgrade(conn, config) -> None:
    config.attributes["connection"] = conn
    upgrade(config, "head")


async def run_db_migrations(connection_string: str, debug_mode: bool) -> None:
    """Run db migrations"""

    logger = get_logger()
    logger.info("Starting run db migrations")

    # retrieves the directory that *this* file is in
    migrations_dir = os.path.dirname(os.path.realpath(__file__))
    # this assumes the alembic.ini is also contained in this same directory
    config_file = os.path.join(migrations_dir, "alembic.ini")
    config = Config(file_=config_file)

    engine = create_async_engine(connection_string, echo=debug_mode)
    async with engine.begin() as conn:
        await conn.run_sync(run_upgrade, config)

    # insert data into the database
    await caller.insert_callers(engine)

    logger.info("Completed run db migrations")
