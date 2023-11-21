from .base import Definition, Entry, Parser
from .cedict import CEDICTParser
from .parse import parse_dict

__all__ = [
    "Entry",
    "Parser",
    "Definition",
    "CEDICTParser",
    "parse_dict",
]
