from advanced_alchemy.extensions.litestar import SQLAlchemyDTO
from litestar import Controller, get
from litestar.dto import DTOConfig
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.controller.base import D, d
from app.db.model import Example, Lexeme, lexeme_example


class LexemeDTO(SQLAlchemyDTO[Lexeme]):
    config = DTOConfig(exclude={"collections"})


class LexemeController(Controller):
    path = "/lexemes"
    return_dto = LexemeDTO

    @get("/{lex_id:str}")
    async def get_lexeme(self, tx: AsyncSession, lex_id: str) -> D[Lexeme]:
        query = select(Lexeme).where(Lexeme.id == lex_id)
        return d((await tx.scalars(query)).one())

    # XXX: Untested with real data
    @get("/{lex_id:str}/examples", return_dto=SQLAlchemyDTO[Example])
    async def get_lexeme_example(
        self,
        tx: AsyncSession,
        lex_id: str,
    ) -> D[list[Example]]:
        query = (
            select(Example).join(lexeme_example).join(Lexeme).where(Lexeme.id == lex_id)
        )

        return d(await tx.scalars(query))
