from litestar.contrib.sqlalchemy.base import UUIDBase
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from tqdm import tqdm

from resources.collections import parse_collection
from resources.dictionary import Entry, parse_dict
from resources.text import parse_text

from .connection import get_engine, session_maker
from .model import Collection, Definition, Dictionary, Lexeme, Text


async def migrate_schema(engine: AsyncEngine = None, drop=False):
    func = UUIDBase.metadata.drop_all if drop else UUIDBase.metadata.create_all
    async with engine.begin() as conn:
        await conn.run_sync(func)


async def seed_dict(sources: list[str]):
    engine = get_engine()
    for source in sources:
        entries = parse_dict(source)
        session = session_maker(bind=engine)
        async with session.begin():
            d = await Dictionary.add_ignore_exists(session, source)
            add_entries(session, entries, d)


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
    for source in sources:
        name, words = parse_collection(source)
        session = session_maker(bind=engine)
        collections = []
        async with session.begin():
            coll = Collection(name=name)

            coll_lexemes = []
            for x in tqdm(words, desc=f"Seeding {source}"):
                lexemes = await Lexeme.find(session, x.zh_sc, x.zh_tc)
                if not lexemes:
                    lexemes = [Lexeme(zh_sc=x.zh_sc, zh_tc=x.zh_tc)]

                coll_lexemes.extend(lexemes)

            coll.lexemes = coll_lexemes
            collections.append(coll)
            session.add_all(collections)


async def seed_text(sources: list[str]):
    engine = get_engine()
    for source in sources:
        texts = []
        for title, text in parse_text(source):
            texts.append(Text(title=title, text=text))

        session = session_maker(bind=engine)
        async with session.begin():
            session.add_all(texts)
