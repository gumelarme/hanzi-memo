import inspect
import re
from dataclasses import dataclass, field
from typing import Callable

from async_lru import alru_cache
from litestar import get
from litestar.dto import DataclassDTO
from litestar.exceptions import ValidationException

from lipotes.dictionary.controller.lexeme import LexemeOut
from lipotes.dictionary.tables import Lexeme
from lipotes.dictionary.tokenizer import tokenizer


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


Point = tuple[int, int]


def find_all_substr_combination(
    positions: list[Point], paths: list[list[Point]]
) -> list[list[Point]]:
    """
    Find all possible combination of substrings
    When tokenizing a sentences with jieba, sometimes some token (lexeme) are not found in the database,
    but we still want to return something useful to the user.
    jieba.tokenize with mode="search" will return much  smaller token that this function will process.

    Example:
    # >>> list(jieba.tokenize("清华大学", mode="search"))
        [('清华', 0, 2), ('华大', 1, 3), ('大学', 2, 4), ('清华大学', 0, 4)]
    the two last integer are the position of the substring
    Possible combination are:
    - [(0, 4)]
    - [(0, 2), (2, 4)] # this one is preferred
    Point (1, 3) is not included because there is no other substring connecting to it.
    """
    if not paths:
        paths = [[x] for x in positions if x[0] == 0]

    found_new = []
    new_path = []
    for p in paths:
        new = False
        tail_end = p[-1][1]
        for pos in positions:
            if tail_end == pos[0]:
                new_path.append([*p, pos])
                new = True

        found_new.append(new)
        if not new:
            new_path.append(p)

    if not any(found_new):
        return paths

    return find_all_substr_combination(positions, new_path)


def avg_token_size(tokens: list[Point]):
    return sum([y - x for x, y in tokens]) / len(tokens)


def find_possible_cut(text: str) -> list[list[str]]:
    tokens = list(tokenizer.tokenize(text, mode="search"))

    # there is no way to cut it
    if len(tokens) == 1:
        return [[text]]

    token_positions = [
        (x, y) for _substr, x, y in tokens if y - x < len(text)
    ]  # get substr positions

    combinations = find_all_substr_combination(token_positions, [])
    combinations = [
        x for x in combinations if x[-1][1] == len(text)
    ]  # filter out incomplete combination

    result = []
    for combo in sorted(combinations, key=avg_token_size, reverse=True):
        combo_str = [text[start:end] for start, end in combo]
        result.append(combo_str)
    return result


async def cut_by_largest_available_lexeme(text: str) -> list[str]:
    tokens_list = find_possible_cut(text)
    for tokens in tokens_list:
        is_found = [bool(await Lexeme.find(token)) for token in tokens]
        if all(is_found):
            return tokens
    else:
        return tokens_list[0]
