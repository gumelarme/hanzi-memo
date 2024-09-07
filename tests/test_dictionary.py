import pytest

from lipotes.dictionary.text_processor import find_repeating, segment_by_position
from lipotes.dictionary.text_processor.segmenter import (
    fill_up_incomplete_path,
    find_ascii,
)


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
