from litestar.contrib.sqlalchemy.base import UUIDBase
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from dictionary.parser import parse, Entry
from .connection import get_engine, session_maker
from .model import Collection, Lexeme, Definition


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
            coll = await Collection.add_ignore_exists(session, source)
            add_entries(session, entries, coll)


def add_entries(session: AsyncSession, entries: list[Entry], coll: Collection):
    lexemes = []
    for e in entries:
        definitions = []
        for d in e.definitions:
            definitions.append(Definition(
                text=d.text,
                category=d.category,
            ))

        lexemes.append(Lexeme(
            zh_sc=e.zh_sc,
            zh_tc=e.zh_tc,
            pinyin=e.pinyin,
            collection=coll,
            definitions=definitions,
        ))

    session.add_all(lexemes)

