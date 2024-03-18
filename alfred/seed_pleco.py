import glob
from pathlib import Path

from sqlalchemy import select
from tqdm import tqdm

from app.db.connection import get_engine, session_maker
from app.db.model import Collection, Lexeme
from resources.collections.pleco import parse_pleco

from .command import Command


class SeedPlecoCommand(Command):
    @classmethod
    async def run(cls, args: list[str]):
        session = session_maker(bind=get_engine())
        collections = parse_pleco(args[0])
        async with session.begin():
            for coll_name, words in collections.items():
                coll = Collection(name=coll_name)
                coll_lexeme = []
                for word in tqdm(words, desc=f"Seeding collection `{coll_name}`"):
                    lexeme_ids = await Lexeme.find_id(
                        session, sc=word.zh_sc, tc=word.zh_tc, pinyin=word.pinyin
                    )

                    if len(lexeme_ids) > 1:
                        print(f"DEBUG: Found multiple lexeme for {word}")
                        print(lexeme_ids)

                    if not lexeme_ids:
                        lexeme_objects = [
                            Lexeme(
                                zh_sc=word.zh_sc, zh_tc=word.zh_tc, pinyin=word.pinyin
                            )
                        ]
                    else:
                        query = select(Lexeme).where(Lexeme.id.in_(lexeme_ids))
                        lexeme_objects = (await session.scalars(query)).all()

                    coll_lexeme.append(lexeme_objects[0])
                coll.lexemes = coll_lexeme
                session.add(coll)

    @classmethod
    def help(cls, command=None) -> str:
        pleco_files = glob.glob("resources/collections/data/source/*.xml")
        pleco_files = [f"  - {Path(x).name}" for x in pleco_files]

        return "\n".join(
            [
                "Commands:",
                f"  - {command} pleco-xml-backup-file",
                "",
                "Available Files:",
                "\n".join(pleco_files),
            ]
        )
