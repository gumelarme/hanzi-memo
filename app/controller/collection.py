from dataclasses import dataclass

from litestar import Controller, get
from litestar.dto import DataclassDTO
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.controller.base import D, d
from app.controller.lexeme import LexemeDTO
from app.controller.pinyin import LexemeOut
from app.db.model import Collection, Lexeme, lexeme_collection


@dataclass
class CollectionD:
    id: str
    name: str
    preview: list[LexemeOut]

    @classmethod
    def from_orm(cls, coll: Collection, lexemes: list[Lexeme] = None):
        lexemes = [] if lexemes is None else lexemes
        return CollectionD(
            id=coll.id,
            name=coll.name,
            preview=[LexemeOut.from_lexeme(x) for x in lexemes],
        )


class CollectionController(Controller):
    path = "/collections"
    return_dto = DataclassDTO[CollectionD]

    @get("/")
    async def get_collections(self, tx: AsyncSession) -> D[list[CollectionD]]:
        collections = []
        query = (
            select(Collection)
            .where(Collection.user_id.is_(None))
            .order_by(Collection.name)
            .limit(100)
        )

        coll: Collection
        for coll in (await tx.scalars(query)).all():
            lexemes = await CollectionController._lexeme_collection(tx, coll.id, 10)
            collections.append(CollectionD.from_orm(coll, lexemes))

        return d(collections)

    @classmethod
    async def _lexeme_collection(
        cls, tx: AsyncSession, coll_id: str, limit: int = 100
    ) -> list[Lexeme]:
        query = (
            select(Lexeme)
            .join(lexeme_collection)
            .join(Collection)
            .where(Collection.id == coll_id)
            .fetch(limit)
        )

        result = await tx.scalars(query)
        return list(result.all())

    @get("/{coll_id:str}")
    async def get_collection_by_id(
        self,
        tx: AsyncSession,
        coll_id: str,
    ) -> D[Collection]:
        query = select(Collection).where(Collection.id == coll_id)
        result = await tx.scalar(query)
        return d(
            CollectionD.from_orm(
                result, await CollectionController._lexeme_collection(tx, coll_id)
            )
        )

    @get("/{coll_id:str}/lexemes", return_dto=LexemeDTO)
    async def get_lexeme_by_collection(
        self,
        tx: AsyncSession,
        coll_id: str,
    ) -> D[list[LexemeOut]]:
        lexemes = await CollectionController._lexeme_collection(tx, coll_id, 100)
        return d([LexemeOut.from_lexeme(x) for x in lexemes])
