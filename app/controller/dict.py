from dataclasses import dataclass

from litestar import get
from litestar.dto import DTOConfig, DataclassDTO
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.model import Collection


@dataclass
class User:
    email: str


@dataclass
class CollectionDTO:
    name: str
    user: User | None


class ReadDTO(DataclassDTO[CollectionDTO]):
    config = DTOConfig()


@get("/collections", return_dto=ReadDTO)
async def get_collections(tx: AsyncSession) -> list[CollectionDTO]:
    coll = await tx.scalars(select(Collection))
    return coll.all() # noqa



