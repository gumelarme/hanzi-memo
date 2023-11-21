from litestar.contrib.sqlalchemy.base import UUIDBase
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from dictionary.parser import parse, Entry
from .connection import get_engine, session_maker
from .model import Dictionary, Lexeme, Definition


async def migrate_schema(engine: AsyncEngine = None, drop=False):
    func = UUIDBase.metadata.drop_all if drop else UUIDBase.metadata.create_all
    async with engine.begin() as conn:
        await conn.run_sync(func)


async def seed_dict(sources: list[str]):
    engine = get_engine()
    for source in sources:
        entries = parse(source)
        session = session_maker(bind=engine)
        async with session.begin():
            d = await Dictionary.add_ignore_exists(session, source)
            add_entries(session, entries, d)


def add_entries(session: AsyncSession, entries: list[Entry], dictionary: Dictionary):
    lexemes = []
    for e in entries:
        definitions = []
        for d in e.definitions:
            definitions.append(Definition(
                text=d.text,
                category=d.category,
                dictionary=dictionary,
            ))

        lexemes.append(Lexeme(
            zh_sc=e.zh_sc,
            zh_tc=e.zh_tc,
            pinyin=e.pinyin,
            definitions=definitions,
        ))

    session.add_all(lexemes)

