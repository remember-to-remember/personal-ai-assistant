""" Module for data repository. """

import asyncio
from abc import ABC

from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlalchemy.future import select
from sqlalchemy.orm import exc, joinedload
from structlog import get_logger

from backend.api import config
from backend.api.entities import Caller, CallerModel
from backend.api.sql_migrations import run


class DataRepository(ABC):
    """Class for data repository."""

    engine: AsyncEngine = None

    def __init__(self, connection_string: str, echo: bool, run_db_migrations: bool):
        if run_db_migrations:
            asyncio.run(run.run_db_migrations(connection_string, echo))
        self.engine = create_async_engine(connection_string, echo=echo)

    async def load_caller(self, idp_id: str) -> Caller:
        """Load caller from data repository."""

        logger = get_logger().bind(idp_id=idp_id)
        logger.info("Starting load caller")

        async_session = async_sessionmaker(self.engine, expire_on_commit=False)
        async with async_session() as session:
            try:
                caller = await session.execute(
                    select(Caller).filter_by(idp_id=idp_id)
                ).scalar_one_or_none()
                CallerModel.model_validate(caller)
            except ValidationError as error:
                logger.error(
                    error,
                    stack_info=config.CONFIG.debug_mode,
                    exc_info=config.CONFIG.debug_mode,
                )
                raise None
            except exc.MultipleResultsFound as error:
                logger.error(
                    error,
                    stack_info=config.CONFIG.debug_mode,
                    exc_info=config.CONFIG.debug_mode,
                )
                return None

        logger.info("Completed load caller")
        return caller
