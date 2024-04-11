from tqdm import tqdm

from lipotes.collection.parser import ZHWord
from lipotes.collection.tables import Collection, LexemeCollection
from lipotes.dictionary.tables import Lexeme


async def seed_collection(name: str, words: list[ZHWord], clause: list[str]):
    coll_lexemes = []
    missing_lexeme = Lexeme.insert()

    for word in tqdm(words, leave=False, desc=f"Seeding collection {name!r}"):
        where = []
        for column in clause:
            where.append(getattr(Lexeme, column) == getattr(word, column))

        lexemes = await Lexeme.objects().where(*where)
        if len(lexemes) > 1:
            breakpoint()

        if not lexemes:
            # NOTE: this will create lexeme that are mentioned in the collections
            # but not exists in the database.
            # The lexeme added have no definitions.
            # TODO: Add it to missing_lexeme tables, with reason/source and hits column
            lex = Lexeme(zh_sc=word.zh_sc, zh_tc=word.zh_tc, pinyin=word.pinyin)
            lexemes = [lex]
            missing_lexeme.add(lex)

        coll_lexemes.extend(lexemes)

    # noinspection PyProtectedMember
    if missing_lexeme.add_delegate._add:
        await missing_lexeme.run()

    bulk_insert = LexemeCollection.insert()
    # TODO: Add owner to collection, so it doesn't override user defined dict
    coll = await Collection.objects().get_or_create(Collection.name == name)
    for lex in coll_lexemes:
        bulk_insert.add(LexemeCollection(collection=coll, lexeme=lex))
    await bulk_insert.run()
