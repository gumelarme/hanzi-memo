from dataclasses import dataclass

from litestar import get
from litestar.dto import DTOConfig, DataclassDTO
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.model import Dictionary


@dataclass
class User:
    email: str


@dataclass
class Dictionary:
    name: str
    user: User | None


class ReadDTO(DataclassDTO[Dictionary]):
    config = DTOConfig()


@get("/dicts", return_dto=ReadDTO)
async def get_dictionaries(tx: AsyncSession) -> list[Dictionary]:
    dicts = await tx.scalars(select(Dictionary))
    return dicts.all() # noqa



