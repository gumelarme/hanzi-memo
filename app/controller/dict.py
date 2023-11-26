from advanced_alchemy.extensions.litestar import SQLAlchemyDTO
from litestar import Controller, get
from litestar.dto import DTOConfig
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.controller.base import D, d
from app.db.model import Dictionary


class DictionaryDTO(SQLAlchemyDTO[Dictionary]):
    name: str

    config = DTOConfig(exclude={"user", "definitions"})


class DictionaryController(Controller):
    @get("/dicts", return_dto=DictionaryDTO)
    async def get_dictionaries(self, tx: AsyncSession) -> D[list[Dictionary]]:
        dicts = await tx.scalars(select(Dictionary))
        return d(dicts.all())  # noqa
