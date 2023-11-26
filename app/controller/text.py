from advanced_alchemy.extensions.litestar import SQLAlchemyDTO
from litestar import Controller, get
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.controller.base import D, d
from app.db.model import Text


class TextController(Controller):
    path = "/texts"
    return_dto = SQLAlchemyDTO[Text]

    @get("")
    async def get_texts(self, tx: AsyncSession) -> D[list[Text]]:
        query = select(Text).limit(100)
        return d((await tx.scalars(query)).all())

    @get("/{text_id:str}")
    async def get_one_text(self, tx: AsyncSession, text_id: str) -> D[Text]:
        query = select(Text).where(Text.id == text_id)
        return d((await tx.scalars(query)).one())
