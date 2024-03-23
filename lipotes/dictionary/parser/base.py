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
    @abstractmethod
    def parse(cls, filename: str) -> list[Entry]:
        raise NotImplementedError
