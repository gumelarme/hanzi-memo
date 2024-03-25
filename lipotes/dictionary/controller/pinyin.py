import inspect
from dataclasses import dataclass, field
from typing import Awaitable, Callable, Generator

from async_lru import alru_cache
from litestar import get
from litestar.dto import DataclassDTO
from litestar.exceptions import ValidationException

from lipotes.dictionary.controller.lexeme import LexemeOut
from lipotes.dictionary.tables import Lexeme
from lipotes.dictionary.tokenizer import tokenizer


@dataclass
class PinyinOut:
    segment: str
    pinyins: list[LexemeOut] = field(default_factory=list)
    is_visible: bool = True


CHAR_LIMIT = 1000


@get("/pinyins/{text:str}", return_dto=DataclassDTO[PinyinOut])
async def get_pinyin(text: str) -> list[PinyinOut]:
    if len(text) > CHAR_LIMIT:
        raise ValidationException(
            detail="Character limit exceeded",
            extra={"zh_query": f"maximum allowed character: {CHAR_LIMIT}"},
        )

    # TODO: Handle ascii tokens
    # TODO: Detect repeating character early to improve performance
    # on long repeating character for example:  哈 x100
    # jieba will cut this into 3 char x 33 times, this make a lot of unnecessary iteration,
    # it shown in increase 200ms response time even with caching

    results: list[str | PinyinOut] = []
    for segmenter in [tokenizer.cut, repeating_token_segmenter, str]:
        target = results if results else [text]
        results = await segment(target, segmenter)

    return results


Segmenter = Callable[[str], list[str] | Generator[str, any, None]] | Awaitable


async def segment(
    texts: list[str | PinyinOut], segmenter: Segmenter
) -> list[str | PinyinOut]:
    result = []
    for text in texts:
        if isinstance(text, PinyinOut):
            result.append(text)
            continue

        if inspect.iscoroutinefunction(segmenter):
            segments = await segmenter(text)
        else:
            segments = segmenter(text)

        for seg in segments:
            lexemes = await Lexeme.find(seg)
            if not lexemes:
                result.append(seg)
                continue

            result.append(
                PinyinOut(segment=seg, pinyins=[LexemeOut(**x) for x in lexemes])
            )
    return result


MAX_REPEATING = 3


@alru_cache(maxsize=2**7)
async def get_possible_repeat(text: str):
    max_len = min(MAX_REPEATING, len(text))
    trial_words = [text[0] * length for length in range(1, max_len)]
    possible_word = await (
        Lexeme.select(Lexeme.zh_sc)
        .where(Lexeme.zh_sc.is_in(trial_words))
        .group_by(Lexeme.zh_sc)
    )
    possible_words_length = [len(word["zh_sc"]) for word in possible_word]

    return possible_words_length


async def repeating_token_segmenter(text: str) -> list[str]:
    # If it's not repeating return the original text
    if len(text) <= 1 or text != len(text) * text[0]:
        return [text]

    possible_words_length = await get_possible_repeat(text)
    step = max(possible_words_length)
    char = text[0]
    length = len(text)
    return ([char * step] * (length // step)) + [char * (length % step)]
