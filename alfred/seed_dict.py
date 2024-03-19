from math import ceil

from sqlalchemy.ext.asyncio import AsyncSession
from tqdm import tqdm

from lipotes.db.connection import get_engine, session_maker
from lipotes.db.model import Definition, Dictionary, Lexeme
from resources.dictionary import Entry, parse_dict
from resources.dictionary.parse import PARSER_FILE_PAIR

from .command import Command
from .utils import chunkify


class SeedDictCommand(Command):
    DICT_CHUNK_SIZE = 5000

    @classmethod
    async def run(cls, args: list[str]):
        source, start, end = cls.parse_args(args)
        await cls.seed(source, start, end)

    @classmethod
    def parse_args(cls, args: list[str]) -> tuple[str, int, int | None]:
        source, *start_end = args
        start = int(start_end[0]) if len(start_end) > 0 else 0
        end = int(start_end[1]) if len(start_end) > 1 else None
        return source, start, end

    @classmethod
    async def seed(cls, source: str, start: int = 0, end: int | None = 0):
        engine = get_engine()

        start = max(start, min(0, start))
        end = end if end is None else max(start, end)

        print(f"Seeding dict {start}:{end}")
        print(f"Splitting dicts into chunks of {cls.DICT_CHUNK_SIZE}")

        entries = parse_dict(source)[start:end]
        chunks = chunkify(entries, cls.DICT_CHUNK_SIZE)
        count = ceil(len(entries) / cls.DICT_CHUNK_SIZE)
        session = session_maker(bind=engine)
        async with session.begin():
            for i, chunk in enumerate(chunks):
                d = await Dictionary.add_ignore_exists(session, source)
                print(f"Adding {i + 1} of {count}...")
                cls.add_entries(session, chunk, d)

    @classmethod
    def add_entries(
        cls, session: AsyncSession, entries: list[Entry], dictionary: Dictionary
    ):
        lexemes = []
        for e in tqdm(entries, desc=f"Seeding {dictionary.name}"):
            definitions = []
            for d in e.definitions:
                definitions.append(
                    Definition(
                        text=d.text,
                        category=d.category,
                        dictionary=dictionary,
                    )
                )

            lexemes.append(
                Lexeme(
                    zh_sc=e.zh_sc,
                    zh_tc=e.zh_tc,
                    pinyin=e.pinyin,
                    definitions=definitions,
                )
            )

        print("Finishing up..")
        session.add_all(lexemes)

    @classmethod
    def help(cls, command="seed-dict") -> str:
        dicts = cls.get_dict_info()
        available_dicts = [f"  - {d}" for d in dicts]
        return "\n".join(
            [
                "Commands:",
                f"  - {command} dict-name [start] [end]",
                "",
                "Available dictionaries: ",
                *available_dicts,
            ]
        )

    @classmethod
    def get_dict_info(cls) -> list[str]:
        # TODO: check if the dict already downloaded
        # TODO: show how many entries are there

        return list(PARSER_FILE_PAIR.keys())
