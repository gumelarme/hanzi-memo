import inspect
import re
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

    # on long repeating character for example:  哈 x100
    # jieba will cut this into 3 char x 33 times, this make a lot of unnecessary iteration,
    # it shows an increase of 200ms response time even with caching
    segments = []
    for segment, is_repeating in segment_repeating(text):
        if is_repeating:
            tokenized = await segment_repeating_char_by_longest_possible_lexeme(segment)
        else:
            tokenized = tokenizer.cut(segment)
        segments.extend(tokenized)

    result = []
    for segment in segments:
        if segment == "":
            continue

        lexemes = await Lexeme.find(segment)
        pinyins = [] if not lexemes else [LexemeOut(**x) for x in lexemes]

        result.append(
            PinyinOut(
                segment=segment,
                pinyins=pinyins,
            )
        )
    return result


MAX_REPEATING = 3


@alru_cache(maxsize=2**7)
async def get_available_repeating_lexemes_count(text: str) -> list[int]:
    max_len = min(MAX_REPEATING, len(text))
    trial_words = [text[0] * length for length in range(1, max_len)]
    possible_word = await (
        Lexeme.select(Lexeme.zh_sc)
        .where(Lexeme.zh_sc.is_in(trial_words))
        .group_by(Lexeme.zh_sc)
    )
    possible_words_length = [len(word["zh_sc"]) for word in possible_word]

    return possible_words_length


async def segment_repeating_char_by_longest_possible_lexeme(text: str) -> list[str]:
    # If it's not repeating return the original text
    if len(text) <= 1 or text != len(text) * text[0]:
        return [text]

    possible_words_length = await get_available_repeating_lexemes_count(text)
    step = max(possible_words_length)
    char = text[0]
    length = len(text)
    return ([char * step] * (length // step)) + [char * (length % step)]


def find_repeating(zh_text: str, max_repeat: int = None) -> list[tuple[int, int]]:
    if max_repeat is None:
        max_repeat = MAX_REPEATING

    # capture any repeating character that has MAX_REPEAT or more character
    pattern = r"(.)\1{%d,}" % max_repeat
    splits = []
    for match in re.finditer(pattern, zh_text):
        if match.group().isascii():
            # only handle chinese character
            continue

        splits.append(match.span())
    return splits


def segment_repeating(zh_text: str, max_repeat: int = None) -> list[tuple[str, bool]]:
    splits = find_repeating(zh_text, max_repeat)
    if not splits:
        return [(zh_text, False)]

    new_splits = splits.copy()
    # make sure we have every part of the string
    head_start, _ = new_splits[0]
    if head_start != 0:
        new_splits.insert(0, (0, head_start))

    _, tail_end = new_splits[-1]
    if tail_end != len(zh_text):
        new_splits.append((tail_end, len(zh_text)))

    results = []
    point: tuple[int, int]
    for i, point in enumerate(new_splits):
        results.append(point)

        # this fill-in any missing segments between each splitting points
        if i + 1 < len(new_splits) and point[1] != new_splits[i + 1][0]:
            results.append((point[1], new_splits[i + 1][0]))

    return [(zh_text[point[0] : point[1]], point in splits) for point in results]
