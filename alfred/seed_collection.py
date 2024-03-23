from math import ceil

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from tqdm import tqdm

from lipotes.collection.parser import COLL_FILE_PAIR, ZHWord, parse_text_collection
from lipotes.db.connection import get_engine, session_maker
from lipotes.db.model import Collection, Lexeme

from .command import Command
from .utils import chunkify


class SeedCollectionCommand(Command):
    COLLECTION_CHUNK_SIZE = 500

    @classmethod
    async def run(cls, args: list[str]):
        engine = get_engine()
        session = session_maker(bind=engine)
        async with session.begin():
            for source in args:
                parsed = parse_text_collection(source)
                await cls.seed_one_collection(session, parsed)

    @classmethod
    async def seed_one_collection(
        cls, session: AsyncSession, parsed: tuple[str, list[ZHWord]]
    ):
        name, words = parsed
        coll = Collection(name=name)
        coll_lexemes = []

        print(
            f"Splitting collection {name!r} into chunks of {cls.COLLECTION_CHUNK_SIZE}"
        )
        chunks = chunkify(words, cls.COLLECTION_CHUNK_SIZE)
        count = ceil(len(words) / cls.COLLECTION_CHUNK_SIZE)

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

    @classmethod
    def help(cls, command="seed-coll") -> str:
        collections = [f"  - {x}" for x in COLL_FILE_PAIR.keys()]
        return "\n".join(
            [
                "Commands:",
                f"  - {command} collection-1 collection-2 ...." "\n",
                "Available collections",
                "\n".join(collections),
            ]
        )
