from advanced_alchemy.extensions.litestar import SQLAlchemyDTO
from litestar import Controller, get
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.controller.base import D, d
from app.db.model import Preset, Text

exclude_presets = select(Preset.text_id)


class TextController(Controller):
    path = "/texts"
    return_dto = SQLAlchemyDTO[Text]

    @get("/", cache=10 * 60)
    async def get_texts(self, tx: AsyncSession) -> D[list[Text]]:
        query = (
            select(Text)
            .where(Text.id.not_in(exclude_presets))
            .order_by(Text.title)
            .limit(100)
        )

        return d((await tx.scalars(query)).all())

    @get("/{text_id:str}")
    async def get_one_text(self, tx: AsyncSession, text_id: str) -> D[Text]:
        query = select(Text).where(Text.id == text_id, Text.id.not_in(exclude_presets))
        return d((await tx.scalars(query)).one())
