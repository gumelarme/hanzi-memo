from dataclasses import dataclass

import jieba
from litestar import get
from litestar.dto import DataclassDTO
from sqlalchemy import Sequence, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.model import Collection, Lexeme, lexeme_collection


@dataclass
class LexemeOut:
    id: str
    zh_sc: str | None
    zh_tc: str | None
    pinyin: str | None

    @classmethod
    def from_lexeme(cls, lex: Lexeme):
        return LexemeOut(
            id=lex.id,
            zh_sc=lex.zh_sc,
            zh_tc=lex.zh_tc,
            pinyin=lex.pinyin,
        )


@dataclass
class Segment:
    segment: str
    pinyin: list[LexemeOut]
    is_visible: bool = True


@get("/pinyin/{zh:str}", return_dto=DataclassDTO[Segment])
async def get_pinyin(
    tx: AsyncSession,
    zh: str,
    blacklist_collection: str | None,
    blacklist_lexeme: str | None,
) -> list[Segment]:
    blacklist = await get_blacklisted(tx, blacklist_collection, blacklist_lexeme)
    words = []
    for x in jieba.cut(zh):
        lexemes = await Lexeme.find(tx, sc=x)

        # TODO: refactor, too repetitive
        if not lexemes:
            for seg in split_no_repeat(x):
                lexemes = await Lexeme.find(tx, sc=seg)
                words.append(create_segments(seg, lexemes, blacklist))
            continue

        words.append(create_segments(x, lexemes, blacklist))
    return words


def create_segments(
    word: str, lex: list[Lexeme], blacklist: Sequence[Lexeme.id]
) -> Segment:
    visible = any([x.id not in blacklist for x in lex])
    lex_out = [LexemeOut.from_lexeme(x) for x in lex]
    return Segment(segment=word, pinyin=lex_out, is_visible=visible)


async def get_blacklisted(
    tx: AsyncSession, collections: str | None, lexemes: str | None
) -> Sequence[Lexeme.id]:
    if not any([collections, lexemes]):
        return []

    queries = []
    if collections:
        bl_coll = collections.split(",")
        q = (
            select(Lexeme.id)
            .join(lexeme_collection)
            .join(Collection)
            .where(Collection.id.in_(bl_coll))
        )
        queries.append(q)

    if lexemes:
        bl_lex = lexemes.split(",")
        q = select(Lexeme.id).where(Lexeme.id.in_(bl_lex))
        queries.append(q)

    blacklists = []
    for q in queries:
        blacklists.extend((await tx.scalars(q)).all())

    return blacklists


def split_no_repeat(text: str) -> list[str]:
    index = -1
    lex = []
    for tok in jieba.tokenize(text, True):
        w, start, end = tok
        if start <= index:
            continue

        lex.append(w)
        index = end - 1

    # FIXME: might return n < len(text)
    if (joined := "".join(lex)) != text:
        raise Exception(
            f"Failed to split `{text}`({len(text)}), instead got `{joined}` ({len(joined)})"
        )

    return lex
