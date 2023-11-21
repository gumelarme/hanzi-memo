from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Definition:
    text: str
    category: str | None = None


@dataclass
class Entry:
    zh_tc: str | None
    zh_sc: str | None
    pinyin: str
    definitions: list[Definition]


class Parser(ABC):
    @classmethod
    def parse(cls, filename: str) -> list[Entry]:
        with open(filename, "r") as f:
            return cls.parse_text(f.read())

    @classmethod
    @abstractmethod
    def parse_text(cls, text: str) -> list[Entry]:
        raise NotImplementedError
