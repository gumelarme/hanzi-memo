from math import ceil

from litestar.contrib.sqlalchemy.base import UUIDBase
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from tqdm import tqdm

from resources.collections import ZHWord, parse_collection
from resources.dictionary import Entry, parse_dict
from resources.text import parse_text

from .connection import get_engine, session_maker
from .model import Collection, Definition, Dictionary, Lexeme, Text


async def migrate_schema(engine: AsyncEngine = None, drop=False):
    func = UUIDBase.metadata.drop_all if drop else UUIDBase.metadata.create_all
    async with engine.begin() as conn:
        await conn.run_sync(func)


DICT_CHUNK_SIZE = 5000
COLLECTION_CHUNK_SIZE = 500


def _chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


async def seed_dict(source: str, start: int = 0, end: int | None = 0):
    engine = get_engine()

    start = max(start, min(0, start))
    end = end if end is None else max(start, end)

    print(f"Seeding dict {start}:{end}")
    print(f"Splitting dicts into chunks of {DICT_CHUNK_SIZE}")

    entries = parse_dict(source)[start:end]
    chunks = _chunks(entries, DICT_CHUNK_SIZE)
    count = ceil(len(entries) / DICT_CHUNK_SIZE)
    session = session_maker(bind=engine)
    async with session.begin():
        for i, chunk in enumerate(chunks):
            d = await Dictionary.add_ignore_exists(session, source)
            print(f"Adding {i+1} of {count}...")
            add_entries(session, chunk, d)


def add_entries(session: AsyncSession, entries: list[Entry], dictionary: Dictionary):
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


async def seed_collection(sources: list[str]):
    engine = get_engine()
    session = session_maker(bind=engine)
    async with session.begin():
        for source in sources:
            parsed = parse_collection(source)
            await seed_one_collection(session, parsed)


async def seed_one_collection(session: AsyncSession, parsed: tuple[str, list[ZHWord]]):
    name, words = parsed
    coll = Collection(name=name)
    coll_lexemes = []

    print(f"Splitting collection {name!r} into chunks of {COLLECTION_CHUNK_SIZE}")
    chunks = _chunks(words, COLLECTION_CHUNK_SIZE)
    count = ceil(len(words) / COLLECTION_CHUNK_SIZE)

    for i, words in enumerate(chunks):
        print(f"Adding {i + 1} of {count}...")
        for x in tqdm(words):
            lexeme_ids = await Lexeme.find_id(session, x.zh_sc, x.zh_tc)
            if not lexeme_ids:
                lexeme_objects = [Lexeme(zh_sc=x.zh_sc, zh_tc=x.zh_tc)]
            else:
                query = select(Lexeme).where(Lexeme.id.in_(lexeme_ids))
                lexeme_objects = (await session.scalars(query)).all()

            coll_lexemes.extend(lexeme_objects)

        coll.lexemes = coll_lexemes
        session.add(coll)


async def seed_text(sources: list[str]):
    engine = get_engine()
    for source in sources:
        texts = []
        for title, text in parse_text(source):
            texts.append(Text(title=title, text=text))

        session = session_maker(bind=engine)
        async with session.begin():
            session.add_all(texts)
