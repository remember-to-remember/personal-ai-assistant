""" Module for inserting caller data into the database. """

from datetime import UTC, datetime
from uuid import UUID

from backend.api.entities import Caller
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker
from sqlalchemy.future import select


async def insert_callers(engine: AsyncEngine) -> None:
    """Insert caller data into the database."""

    callers = [
        {
            "caller_id": UUID("00000000-0000-0000-0000-000000000000"),
            "name": "WhatsApp for Business",
            "idp_id": "riZ8yYUCrB",
            "email": "whatsapp",
            "first_created": datetime.now(UTC),
            "last_updated": datetime.now(UTC),
        },
        {
            "caller_id": UUID("00000000-0000-0000-0000-000000000001"),
            "name": "Ankur Soni",
            "idp_id": "google-oauth2|103311653287323190363",
            "email": "soniankur@gmail.com",
            "first_created": datetime.now(UTC),
            "last_updated": datetime.now(UTC),
        },
    ]

    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        for caller in callers:
            existing_caller = await session.execute(
                select(Caller).filter_by(caller_id=caller["caller_id"])
            )
            if existing_caller.scalar_one_or_none():
                continue
            session.add(Caller(**caller))
        await session.commit()
