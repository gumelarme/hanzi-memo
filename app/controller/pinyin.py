from dataclasses import dataclass
from typing import Callable, Generator

import jieba
from litestar import get
from litestar.dto import DataclassDTO
from litestar.exceptions import ValidationException
from sqlalchemy import Sequence, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.controller.base import D, d
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
    strict_visible: bool = True


CHAR_LIMIT = 1000


@get("/pinyins/{zh:str}", return_dto=DataclassDTO[Segment])
async def get_pinyin(
    tx: AsyncSession,
    zh: str,
    blacklist_collection: str | None,
    blacklist_lexeme: str | None,
) -> D[list[Segment]]:
    if len(zh) > CHAR_LIMIT:
        raise ValidationException(
            detail="Character limit exceeded",
            extra={"zh": f"maximum allowed character: {CHAR_LIMIT}"},
        )

    blacklist = await get_blacklisted(tx, blacklist_collection, blacklist_lexeme)

    # 1st, intelligent cut
    # 2nd, re-split segments that not found on db
    # 3rd, give up and split by char
    segments = await try_segment(tx, [zh], jieba.cut)
    segments = await try_segment(tx, segments, split_no_repeat)
    segments = await try_segment(tx, segments, list)

    result = []
    for seg in segments:
        if isinstance(seg, str):
            word, lex = seg, []
            visible = False
            strict_visible = False
        else:
            word, lex = seg
            visible = any([x.id not in blacklist for x in lex])
            lex = [LexemeOut.from_lexeme(x) for x in lex]

            strict_visible = visible
            if visible:
                strict_visible = await is_each_char_blacklisted(tx, blacklist, word)

        result.append(Segment(word, lex, visible, strict_visible))

    return d(result)


async def is_each_char_blacklisted(
    tx: AsyncSession,
    blacklist: Sequence[Lexeme],
    word: str,
) -> bool:
    """
    each char might be in a collection, but the combinations doesn't
    this assumes if individual char are learned, then the combinations is also learned
    """
    each_char_lexemes = [await Lexeme.find(tx, x) for x in list(word)]
    each_char_found = []
    for lexemes in each_char_lexemes:
        each_char_found.append(any([x.id in blacklist for x in lexemes]))
    return not all(each_char_found)


MaybeSegment = str | tuple[str, list[Lexeme]]
Cutter = Callable[[str], Generator[str, any, None] | list[str]]


async def try_segment(
    tx: AsyncSession, texts: list[MaybeSegment], method: Cutter
) -> list[MaybeSegment]:
    result: list[MaybeSegment] = []
    for text in texts:
        if isinstance(text, tuple):
            result.append(text)
            continue

        for word in method(text):
            lexemes = await Lexeme.find(tx, sc=word)
            if not lexemes:
                result.append(word)
                continue

            result.append((word, lexemes))

    return result


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
