import re
from dataclasses import dataclass
from typing import Callable, Generator
from uuid import UUID

import jieba
from litestar import Request, get
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


@get("/pinyins/{zh:str}", return_dto=DataclassDTO[Segment], cache=60 * 3)
async def get_pinyin(
    request: Request,
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

    try:
        segments = await try_segment(tx, segments, split_no_repeat)
    except Exception as e:
        segments = await try_segment(tx, segments, lambda x: split_no_repeat(x, True))
        request.logger.exception(e)
        request.logger.error("failed on split_no_repeat", segments=segments)

    segments = await try_segment(tx, segments, split_if_chinese)

    result = []
    for seg in segments:
        if isinstance(seg, str):
            word, lex_outs = seg, []
            visible = False
            strict_visible = False
        else:
            word, lex_ids = seg
            visible = any([x not in blacklist for x in lex_ids])

            lex_outs = []
            for l_id in lex_ids:
                lexeme = await tx.get(Lexeme, l_id)
                if lexeme is None:
                    raise Exception("Lexeme not found with find by id ")

                lex_outs.append(LexemeOut.from_lexeme(lexeme))  # noqa

            strict_visible = visible
            if visible:
                strict_visible = await is_each_char_blacklisted(tx, blacklist, word)

        result.append(Segment(word, lex_outs, visible, strict_visible))

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
    each_char_lexemes = [await Lexeme.find_id(tx, x) for x in list(word)]
    each_char_found = []
    for lexemes in each_char_lexemes:
        each_char_found.append(any([x in blacklist for x in lexemes]))
    return not all(each_char_found)


MaybeSegment = str | tuple[str, list[UUID]]
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
            lexemes = await Lexeme.find_id(tx, sc=word)
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


def split_no_repeat(text: str, gracefully=False) -> list[str]:
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
        if not gracefully:
            raise Exception(
                f"Failed to split `{text}`({len(text)}), instead got `{joined}` ({len(joined)})"
            )
        else:
            return [text]

    return lex


RE_ASCII = re.compile(r"[ -~]+")


def split_if_chinese(text: str) -> list[str]:
    if RE_ASCII.match(text):
        return [text]

    return list(text)
