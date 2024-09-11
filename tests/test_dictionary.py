import piccolo.table
import pytest

from lipotes.dictionary.controller.pinyin import split_if_not_ascii
from lipotes.dictionary.tables import Lexeme
from lipotes.dictionary.text_processor import find_repeating, segment_by_position
from lipotes.dictionary.text_processor.segmenter import (
    fill_up_incomplete_path,
    find_ascii,
    get_available_repeating_lexemes_count,
    segment_repeating_char_by_longest_possible_lexeme,
)
from lipotes.dictionary.text_processor.tokenizer import (
    avg_token_size,
    cut_by_largest_available_lexeme,
    find_all_substr_combination,
    find_possible_cut,
)

pytest_plugins = ("pytest_asyncio",)


@pytest.mark.parametrize(
    "text,expected",
    [
        ("我是你爸爸哈哈哈", [(5, 8)]),
        ("啦啦啦你啦啦啦", [(0, 3), (4, 7)]),
        ("啦啦啦BBBB啦啦啦啦", [(0, 3), (7, 11)]),
    ],
)
def test_find_repeating(text, expected):
    repeats = find_repeating(text, max_repeat=2)
    assert repeats == expected


@pytest.mark.parametrize(
    "splits,length,expect",
    [
        ([(0, 1), (8, 9)], 10, [(0, 1), (1, 8), (8, 9), (9, 10)]),
        ([(1, 2)], 5, [(0, 1), (1, 2), (2, 5)]),
    ],
)
def test_fill_up_incomplete_path(splits, length, expect):
    assert fill_up_incomplete_path(splits, length) == expect


def test_segment_by_position():
    text_1 = "Hello"
    assert segment_by_position(text_1, []) == [(text_1, False)]

    text_2 = "ABCDEFG"
    assert segment_by_position(
        text_2,
        [
            (0, 1),
            (1, 3),
            (3, 7),
        ],
    ) == [
        ("A", True),
        ("BC", True),
        ("DEFG", True),
    ]


@pytest.mark.parametrize(
    "text, expect",
    [
        ("ABC", [(0, 3)]),
        ("你好I'am gugum", [(2, 12)]),
        ("你I'am gugum好", [(1, 11)]),
        ("你 好", [(1, 2)]),
        ("你.好", [(1, 2)]),
    ],
)
def test_find_ascii(text, expect):
    assert find_ascii(text) == expect


@pytest.fixture()
def setup_db():
    tables = [Lexeme]
    piccolo.table.create_db_tables_sync(*tables)
    yield
    piccolo.table.drop_db_tables_sync(*tables)


def clear_cache(cached_method):
    try:
        cached_method.__closure__[0].cell_contents.clear()
    except (AttributeError, IndexError) as e:
        raise Exception(
            f"Failed to clear cached method: `{cached_method.__name__}`"
        ) from e


@pytest.mark.parametrize(
    "entries,expect",
    [
        ([Lexeme(zh_sc="哈", zh_tc="哈", pinyin="ha1")], [1]),
        (
            [
                Lexeme(zh_sc="哈", zh_tc="哈", pinyin="ha1"),
                Lexeme(zh_sc="哈" * 2, zh_tc="哈" * 2, pinyin="ha1" * 2),
            ],
            [1, 2],
        ),
        (
            [
                Lexeme(zh_sc="哈", zh_tc="哈", pinyin="ha1"),
                Lexeme(zh_sc="哈" * 2, zh_tc="哈" * 2, pinyin="ha1" * 2),
                Lexeme(zh_sc="哈" * 3, zh_tc="哈" * 3, pinyin="ha1" * 3),
            ],
            [1, 2, 3],
        ),
        (
            [
                Lexeme(zh_sc="哈", zh_tc="哈", pinyin="ha1"),
                Lexeme(zh_sc="哈" * 3, zh_tc="哈" * 3, pinyin="ha1" * 3),
            ],
            [1, 3],
        ),
    ],
)
@pytest.mark.asyncio
async def test_get_get_available_repeating_lexemes_count(setup_db, entries, expect):
    clear_cache(get_available_repeating_lexemes_count)
    Lexeme.insert(*entries).run_sync()
    assert (await get_available_repeating_lexemes_count("哈哈哈哈哈哈")) == expect


@pytest.mark.asyncio
async def test_segment_repeating_char_by_longest_possible_lexeme(setup_db):
    assert await segment_repeating_char_by_longest_possible_lexeme("你好") == [
        "你好"
    ], "Non repeating chars should return itself"

    clear_cache(get_available_repeating_lexemes_count)
    Lexeme.insert(
        Lexeme(zh_sc="哈", zh_tc="哈", pinyin="ha1"),
    ).run_sync()
    assert await segment_repeating_char_by_longest_possible_lexeme("哈哈哈") == ["哈"] * 3

    clear_cache(get_available_repeating_lexemes_count)
    Lexeme.insert(
        Lexeme(zh_sc="哈" * 2, zh_tc="哈" * 2, pinyin="ha1" * 2),
    ).run_sync()
    assert await segment_repeating_char_by_longest_possible_lexeme("哈哈哈") == ["哈哈", "哈"]


def test_avg_token_size():
    assert avg_token_size([(2, 10)]) == 8
    assert avg_token_size([(1, 2), (3, 4)]) == 1
    assert avg_token_size([(1, 5), (6, 17), (17, 20)]) == 6
    assert avg_token_size([(1, 5), (6, 17), (17, 18), (18, 20)]) == 4.5


def test_find_all_substr_combination():
    assert find_all_substr_combination(
        [
            (0, 1),
            (1, 4),
        ],
        [],
    ) == [[(0, 1), (1, 4)]]

    assert find_all_substr_combination(
        [
            (0, 1),
            (3, 4),
            (1, 4),
        ],
        [],
    ) == [[(0, 1), (1, 4)]], "Dangling substr should be ignored"

    assert find_all_substr_combination(
        [
            (0, 1),
            (1, 2),
            (2, 4),
            (1, 4),
        ],
        [],
    ) == [
        [(0, 1), (1, 2), (2, 4)],
        [(0, 1), (1, 4)],
    ], "Multiple combinations of path didnt match"

    assert find_all_substr_combination(
        [
            (0, 2),
            (2, 4),
            (0, 4),
        ],
        [],
    ) == [
        [(0, 2), (2, 4)],
        [(0, 4)],
    ], "Multiple combinations of path, where one is the whole string"


@pytest.mark.parametrize(
    "text,expect",
    [
        ("你好", [["你好"]]),
        ("你好我是", [["你好", "我", "是"]]),
        ("清华大学", [["清华", "大学"], ["清", "华大", "学"]]),
        (
            "第十一次",
            [
                ["第十", "一次"],
                ["第十一", "次"],
                ["第", "十一次"],
                ["第", "十一", "次"],
            ],
        ),
    ],
)
def test_find_possible_cut(text, expect):
    assert all(combo in expect for combo in find_possible_cut(text))


# TODO: More test case
@pytest.mark.parametrize(
    "lexemes,query,expect",
    [
        (
            [
                Lexeme(zh_sc="第", zh_tc="第", pinyin="di4"),
                Lexeme(zh_sc="十一", zh_tc="十一", pinyin="shi2yi1"),
                Lexeme(zh_sc="次", zh_tc="次", pinyin="ci4"),
            ],
            "第十一次",
            ["第", "十一", "次"],
        ),
        (
            [
                Lexeme(zh_sc="无", zh_tc="无", pinyin="wu2"),
            ],
            "第十一次",
            ["第十", "一次"],
        ),
    ],
)
@pytest.mark.asyncio
async def test_cut_by_largest_available_lexeme(setup_db, lexemes, query, expect):
    Lexeme.insert(*lexemes).run_sync()
    clear_cache(Lexeme.find)
    assert (await cut_by_largest_available_lexeme(query)) == expect


def test_split_if_not_ascii():
    assert split_if_not_ascii("Hello") == ["Hello"]
    assert split_if_not_ascii("你好") == ["你", "好"]
