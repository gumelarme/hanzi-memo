import inspect
from dataclasses import dataclass, field
from typing import Callable

from litestar import get
from litestar.dto import DataclassDTO
from litestar.exceptions import ValidationException

from lipotes.dictionary.controller.lexeme import LexemeOut
from lipotes.dictionary.tables import Lexeme
from lipotes.dictionary.text_processor import (
    cut_by_largest_available_lexeme,
    segment_repeating,
    segment_repeating_char_by_longest_possible_lexeme,
    tokenizer,
)


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

    # on long repeating character for example:  哈 x100
    # jieba will cut this into 3 char x 33 times, this make a lot of unnecessary iteration,
    # it shows an increase of 200ms response time even with caching
    segments: list[str] = []
    for segment, is_repeating in segment_repeating(text):
        if is_repeating:
            tokens = await segment_repeating_char_by_longest_possible_lexeme(segment)
        else:
            tokens = [segment]
        segments.extend(tokens)

    for tokenizer_func in [tokenizer.cut, cut_by_largest_available_lexeme, str]:
        segments = await make_pinyin(segments, tokenizer_func)

    # Everything should be a dictionary here
    result = []
    lexemes: PinyinOut
    for lexemes in segments:
        result.append(lexemes)

    return result


async def make_pinyin(
    segments: list[str | PinyinOut],
    tokenizer_: Callable,
) -> list[str | PinyinOut]:
    result = []
    segments = [x for x in segments if x]
    for segment in segments:
        if isinstance(segment, PinyinOut):
            result.append(segment)
            continue

        if inspect.iscoroutinefunction(tokenizer_):
            tokens = await tokenizer_(segment)
        else:
            tokens = tokenizer_(segment)

        for token in tokens:
            lexemes = await Lexeme.find(token)

            if not lexemes:
                # leave it for the next tokenizer to process
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
