import jieba
from advanced_alchemy.extensions.litestar.dto import SQLAlchemyDTO
from litestar import get
from litestar.dto import DTOConfig
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.model import Lexeme


class LexemeDTO(SQLAlchemyDTO[Lexeme]):
    config = DTOConfig(exclude={"examples", "definitions"}, max_nested_depth=100)


# TODO: Change to dict[str, list[Lexeme]]
# it somehow doesnt work, figure it out
@get("/pinyin/{zh:str}", return_dto=LexemeDTO, sync_to_thread=False)
async def get_pinyin(tx: AsyncSession, zh: str) -> list[Lexeme]:
    words = []
    for x in jieba.cut(zh):
        lex = await Lexeme.find(tx, sc=x)
        words.extend(lex)

    return words
