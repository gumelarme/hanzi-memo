import os

from lipotes.collection.tables import Collection, LexemeCollection
from lipotes.dictionary.tables import Lexeme
from resources.collections import COLL_FILE_PAIR, parse_collection


async def seed(collections: str):
    """
    Seed collection tables

    :param collections:
        The collection name separated by comma, see help.
        e.g. hsk1,hsk2
    """

    collections = [x.strip() for x in collections.split(",")]
    try:
        for coll in collections:
            validate_collection(coll)
    except Exception as e:
        print(f"Error: {e}")
        print_available_collections()
        return

    for coll_name in collections:
        name, parsed_collection = parse_collection(coll_name)

        coll_lexemes = []
        missing_lexeme = Lexeme.insert()

        for word in parsed_collection:
            lexemes = await Lexeme.select().where(
                Lexeme.zh_sc == word.zh_tc, Lexeme.zh_tc == word.zh_tc
            )

            if not lexemes:
                # NOTE: this will create lexeme that are mentioned in the collections
                # but not exists in the database.
                # The lexeme added have no definitions.
                # TODO: Add it to missing_lexeme tables, with reason/source and hits column
                lexemes = [
                    Lexeme(zh_sc=word.zh_sc, zh_tc=word.zh_tc, pinyin=word.pinyin)
                ]
                missing_lexeme.add(lexemes[0])
            coll_lexemes.extend(lexemes)

        await missing_lexeme.run()

        bulk_insert = LexemeCollection.insert()

        # TODO: Add owner to collection, so it doesn't override user defined dict
        coll = await Collection.objects().get_or_create(Collection.name == name)
        for lex in coll_lexemes:
            bulk_insert.add(
                LexemeCollection(
                    collection=coll,
                    lexeme=lex,
                )
            )
        await bulk_insert.run()


def validate_collection(collection: str, resource_dir=None) -> None:
    if collection not in COLL_FILE_PAIR:
        raise Exception(f"Collection {collection!r} is not valid")

    if resource_dir is None:
        resource_dir = os.path.join(os.getcwd(), "resources/collections/data/source")

    filename = os.path.join(resource_dir, COLL_FILE_PAIR[collection][1])
    if not os.path.isfile(filename):
        raise Exception(f"File {filename!r} is not exist")


def print_available_collections() -> None:
    # TODO: Print available collections
    pass
