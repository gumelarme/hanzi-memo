import os
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from litestar.datastructures import State
from litestar.exceptions import ClientException
from litestar.status_codes import HTTP_409_CONFLICT
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from litestar import Litestar
from pydantic_settings import BaseSettings, SettingsConfigDict


class DBSettings(BaseSettings):
    user: str
    password: str
    host: str
    port: int
    name: str = "hanzi_memo"

    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_prefix="DB_",
    )


def get_engine():
    s = DBSettings()
    conn_str = f"postgresql+asyncpg://{s.user}:{s.password}@{s.host}:{s.port}/{s.name}"
    return create_async_engine(conn_str, echo=True)


@asynccontextmanager
async def db_connection(app: Litestar) -> AsyncGenerator[None, None]:
    engine = getattr(app.state, "engine", None)
    if engine is None:
        engine = get_engine()
        app.state.engine = engine

    try:
        yield
    finally:
        await engine.dispose()


session_maker = async_sessionmaker(expire_on_commit=True)


async def provide_transaction(state: State) -> AsyncGenerator[AsyncSession, None]:
    async with session_maker(bind=state.engine) as session:
        try:
            async with session.begin():
                yield session
        except IntegrityError as exc:
            raise ClientException(
                status_code=HTTP_409_CONFLICT,
                detail=str(exc),
            ) from exc

