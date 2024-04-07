import re
import string

from async_lru import alru_cache

from lipotes.dictionary.tables import Lexeme

MAX_REPEATING = 3


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


def segment_by_position(
    text: str, splits: list[tuple[int, int]]
) -> list[tuple[str, bool]]:
    if not splits:
        return [(text, False)]

    new_splits = splits.copy()
    # make sure we have every part of the string
    head_start, _ = new_splits[0]
    if head_start != 0:
        new_splits.insert(0, (0, head_start))

    _, tail_end = new_splits[-1]
    if tail_end != len(text):
        new_splits.append((tail_end, len(text)))

    results = []
    point: tuple[int, int]
    for i, point in enumerate(new_splits):
        results.append(point)

        # this fill-in any missing segments between each splitting points
        if i + 1 < len(new_splits) and point[1] != new_splits[i + 1][0]:
            results.append((point[1], new_splits[i + 1][0]))

    return [(text[point[0] : point[1]], point in splits) for point in results]


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


def find_ascii(text: str) -> list[tuple[int, int]]:
    pattern = r"[A-Za-z0-9\s%s]+" % string.punctuation
    return [match.span() for match in re.finditer(pattern, text)]
