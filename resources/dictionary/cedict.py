import re
from .base import Definition, Entry
from . import Parser


class CEDICTParser(Parser):
    skip = 31
    CEDICT_LINE_REGEX = re.compile(r"(.+)(?<!,)\s(.+) \[(.+)] /(.+)/")

    @classmethod
    def parse_text(cls, text: str) -> list[Entry]:
        lines = text.split("\n")
        return [cls.parse_line(line) for line in lines[cls.skip:]]

    @classmethod
    def parse_line(cls, text: str) -> Entry:
        match = cls.CEDICT_LINE_REGEX.match(text)
        tc, sc, pinyin, raw_definition = match.groups()

        definitions = []
        for d in raw_definition.split("/"):
            definitions.append(Definition(text=d))

        normal_pinyin = cls.normalize_pinyin(pinyin)
        return Entry(zh_tc=tc, zh_sc=sc, pinyin=normal_pinyin, definitions=definitions)

    @classmethod
    def normalize_pinyin(cls, text: str) -> str:
        return text.replace("u:", "v") if ":" in text else text





