from advanced_alchemy.extensions.litestar import SQLAlchemyDTO
from litestar import Controller, get
from litestar.dto import DTOConfig
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.controller.base import D, d
from app.db.model import Dictionary, Lexeme


class LexemeDTO(SQLAlchemyDTO[Lexeme]):
    config = DTOConfig(exclude={"collections"})


class LexemeController(Controller):
    path = "/lexemes"
    return_dto = LexemeDTO

    @get("/{lex_id:str}")
    async def get_lexeme(self, tx: AsyncSession, lex_id: str) -> D[Lexeme]:
        query = select(Lexeme).where(Lexeme.id == lex_id)
        return d(await tx.scalar(query))
