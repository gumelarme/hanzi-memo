import structlog
from jieba import Tokenizer

from lipotes.dictionary.tables import Lexeme

log = structlog.get_logger()
tokenizer = Tokenizer()


def init_tokenizer():
    # TODO: add jieba big user dict
    # TODO: add misses word to the tokenizer
    # TODO: add user collection word to tokenizer

    i_am_lipotes = tokenizer.lcut("我是白暨豚")
    log.info("Initializing jieba tokenizer", cuts=i_am_lipotes)


Point = tuple[int, int]


def find_all_substr_combination(
    positions: list[Point], paths: list[list[Point]]
) -> list[list[Point]]:
    """
    | None   Find all possible combination of substrings
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
