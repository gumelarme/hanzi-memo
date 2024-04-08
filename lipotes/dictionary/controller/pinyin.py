import inspect
import re
from dataclasses import dataclass, field
from typing import Callable

from litestar import get
from litestar.dto import DataclassDTO
from litestar.exceptions import ValidationException
from piccolo.columns.combination import WhereRaw

from lipotes.dictionary.controller.lexeme import LexemeOut
from lipotes.dictionary.tables import Lexeme
from lipotes.dictionary.text_processor import (
    cut_by_largest_available_lexeme,
    find_ascii,
    find_repeating,
    segment_by_position,
    segment_repeating_char_by_longest_possible_lexeme,
    tokenizer,
)
from lipotes.dictionary.text_processor.constants import punctuation


@dataclass
class PinyinOut:
    token: str
    pinyins: list[LexemeOut] = field(default_factory=list)
    is_visible: bool = True


CHAR_LIMIT = 1000


@get("/pinyins/{text:str}", return_dto=DataclassDTO[PinyinOut])
async def get_pinyin(text: str) -> list[PinyinOut]:
    if len(text) > CHAR_LIMIT:
        raise ValidationException(
            detail="Character limit exceeded",
            extra={"text": f"maximum allowed character: {CHAR_LIMIT}"},
        )

    segments: list[str] = []
    for s, is_ascii in segment_by_position(text, find_ascii(text)):
        if is_ascii:
            segments.append(s)
            continue

        # on long repeating character for example:  哈 x100
        # jieba will cut this into 3 char x 33 times, this make a lot of unnecessary iteration,
        # it shows an increase of 200ms response time even with caching
        for segment, is_repeating in segment_by_position(s, find_repeating(s)):
            if is_repeating:
                tokens = await segment_repeating_char_by_longest_possible_lexeme(
                    segment
                )
            else:
                tokens = [segment]
            segments.extend(tokens)

    tokenizer_functions = [
        tokenizer.cut,
        cut_by_largest_available_lexeme,
        split_if_not_ascii,
    ]
    for i, func in enumerate(tokenizer_functions):
        segments = await make_pinyin(segments, func, i + 1 == len(tokenizer_functions))

    # Everything should be a dictionary here
    result = []
    lexemes: PinyinOut
    for lexemes in segments:
        result.append(lexemes)

    return result


async def make_pinyin(
    segments: list[str | PinyinOut],
    tokenizer_: Callable,
    is_last: bool = False,
) -> list[str | PinyinOut]:
    result = []
    segments = [x for x in segments if x]
    for segment in segments:
        if isinstance(segment, PinyinOut):
            result.append(segment)
            continue

        if await is_non_token(segment):
            result.append(PinyinOut(token=segment, pinyins=[]))
            continue

        if inspect.iscoroutinefunction(tokenizer_):
            tokens = await tokenizer_(segment)
        else:
            tokens = tokenizer_(segment)

        for token in tokens:
            lexemes = await Lexeme.find(token)

            if not lexemes:
                # leave it for the next tokenizer to process
                token = token if not is_last else PinyinOut(token=token, pinyins=[])
                result.append(token)
                continue

            result.append(
                PinyinOut(
                    token=token,
                    pinyins=[LexemeOut(**x) for x in lexemes],
                    # FIXME: this is a place holder
                    is_visible=True,
                )
            )
    return result


def split_if_not_ascii(text: str):
    return [text] if text.isascii() else text


def get_ascii_lexeme() -> dict[str, dict]:
    lexemes = Lexeme.select().where(WhereRaw("zh_sc ~ '^[A-Za-z0-9]+$'")).run_sync()
    return {lex["zh_sc"]: lex for lex in lexemes}


ASCII_LEXEME = get_ascii_lexeme()


async def is_non_token(text: str) -> bool:
    # skip chinese punctuation
    pattern = r"[%s]" % punctuation
    if re.match(pattern, text):
        return True

    # there are ascii entry on database, e.g. 996, PU
    if text.isascii() and text not in ASCII_LEXEME:
        return True

    return False
