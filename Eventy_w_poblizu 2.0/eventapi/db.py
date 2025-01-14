"""A module providing database access."""

import asyncio

import databases
import sqlalchemy
from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.exc import OperationalError, DatabaseError
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.mutable import MutableList
from asyncpg.exceptions import CannotConnectNowError, ConnectionDoesNotExistError

from eventapi.api.utils.enums import UserRole
from eventapi.config import config

metadata = sqlalchemy.MetaData()

event_table = sqlalchemy.Table(
    "events",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String),
    sqlalchemy.Column("start_time", sqlalchemy.TIMESTAMP(timezone=True)),
    sqlalchemy.Column("end_time", sqlalchemy.TIMESTAMP(timezone=True)),
    sqlalchemy.Column(
        "location_id",
        sqlalchemy.ForeignKey("locations.id"),
        nullable=True,
    ),
    sqlalchemy.Column("max_participants", sqlalchemy.Integer, nullable=True),
    sqlalchemy.Column("user_id", sqlalchemy.ForeignKey("users.id"), nullable=False),
    sqlalchemy.Column("description", sqlalchemy.String, nullable=True),
)

location_table = sqlalchemy.Table(
    "locations",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String),
    sqlalchemy.Column("latitude", sqlalchemy.Float),
    sqlalchemy.Column("longitude", sqlalchemy.Float),
    sqlalchemy.Column("address", sqlalchemy.String, nullable=True),
    UniqueConstraint("latitude", "longitude", name="unique_location_coordinates"),
)

review_table = sqlalchemy.Table(
    "reviews",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("content", sqlalchemy.String, nullable=True),
    sqlalchemy.Column("rating", sqlalchemy.Integer),
    sqlalchemy.Column(
        "user_id",
        sqlalchemy.ForeignKey("users.id"),  # Klucz obcy do tabeli `users`
        nullable=False,
    ),
    sqlalchemy.Column("event_id", sqlalchemy.ForeignKey("events.id"), nullable=False),
)

user_table = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column(
        "id",
        UUID(as_uuid=True),
        primary_key=True,
        server_default=sqlalchemy.text("gen_random_uuid()"),
    ),
    sqlalchemy.Column("username", sqlalchemy.String, unique=True),
    sqlalchemy.Column("email", sqlalchemy.String, unique=True),
    sqlalchemy.Column("password", sqlalchemy.String),
    sqlalchemy.Column("role",sqlalchemy.Enum(UserRole),default=UserRole.USER),
)

db_uri = (
    f"postgresql+asyncpg://{config.DB_USER}:{config.DB_PASSWORD}"
    f"@{config.DB_HOST}/{config.DB_NAME}"
)

engine = create_async_engine(
    db_uri,
    echo=True,
    future=True,
    pool_pre_ping=True,
)

database = databases.Database(
    db_uri,
    force_rollback=True,
)


async def init_db(retries: int = 5, delay: int = 5) -> None:
    """Function initializing the DB.

    Args:
        retries (int, optional): Number of retries of connect to DB.
            Defaults to 5.
        delay (int, optional): Delay of connect do DB. Defaults to 2.
    """
    for attempt in range(retries):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(metadata.create_all)
            return
        except (
            OperationalError,
            DatabaseError,
            CannotConnectNowError,
            ConnectionDoesNotExistError,
        ) as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            await asyncio.sleep(delay)

    raise ConnectionError("Could not connect to DB after several retries.")