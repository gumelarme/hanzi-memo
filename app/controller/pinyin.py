from dataclasses import dataclass

import jieba
from litestar import get
from litestar.dto import DataclassDTO
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.model import Lexeme


@dataclass
class LexemeOut:
    id: str
    zh_sc: str | None
    zh_tc: str | None
    pinyin: str | None

    @classmethod
    def from_lexeme(cls, lex: Lexeme, visible: bool = True):
        return LexemeOut(
            id=lex.id,
            zh_sc=lex.zh_sc,
            zh_tc=lex.zh_tc,
            pinyin=lex.pinyin,
        )


@dataclass
class Segments:
    segment: str
    pinyin: list[LexemeOut]
    is_visible: bool = True


@get("/pinyin/{zh:str}", return_dto=DataclassDTO[Segments])
async def get_pinyin(tx: AsyncSession, zh: str) -> list[Segments]:
    words = []
    for x in jieba.cut(zh):
        lexemes = await Lexeme.find(tx, sc=x)
        lex_out = [LexemeOut.from_lexeme(x) for x in lexemes]
        words.append(Segments(segment=x, pinyin=lex_out))

    return words
