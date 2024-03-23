import os
from typing import Type

from .base import Definition, Entry, Parser
from .cedict import CEDICTParser

PARSER_FILE_PAIR: dict[str, tuple[Type[Parser], str]] = {
    "cedict": (CEDICTParser, "cedict_ts.u8"),
}


def parse_dict(source: str) -> list[Entry]:
    parser, filename = PARSER_FILE_PAIR[source]
    filename = os.path.join(os.getcwd(), "resources/dictionary/source", filename)
    return parser.parse(filename)


__all__ = [
    "Parser",
    "Entry",
    "Definition",
    "CEDICTParser",
    "parse_dict",
    "PARSER_FILE_PAIR",
]
