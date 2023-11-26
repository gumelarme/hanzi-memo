from advanced_alchemy.extensions.litestar import SQLAlchemyDTO
from litestar import Controller, get
from litestar.dto import DTOConfig
from litestar.exceptions import ClientException, HTTPException, NotFoundException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.controller.base import D, d
from app.controller.lexeme import LexemeDTO
from app.db.model import Collection, Lexeme, lexeme_collection


class CollectionDTO(SQLAlchemyDTO[Collection]):
    config = DTOConfig(exclude={"lexemes", "user", "user_id"})


class CollectionController(Controller):
    path = "/collections"
    return_dto = CollectionDTO

    @get("/")
    async def get_collections(self, tx: AsyncSession) -> D[list[Collection]]:
        query = select(Collection).where(Collection.user_id.is_(None)).limit(100)
        return d((await tx.scalars(query)).all())

    @get("/{coll_id:str}")
    async def get_collection_by_id(
        self,
        tx: AsyncSession,
        coll_id: str,
    ) -> D[Collection]:
        query = select(Collection).where(Collection.id == coll_id)
        result = await tx.scalars(query)
        return d(result.one())

    @get("/{coll_id:str}/lexemes", return_dto=LexemeDTO)
    async def get_lexeme_by_collection(
        self,
        tx: AsyncSession,
        coll_id: str,
    ) -> D[list[Lexeme]]:
        query = (
            select(Lexeme)
            .join(lexeme_collection)
            .join(Collection)
            .where(Collection.id == coll_id)
        )

        return d(await tx.scalars(query))
