import os

from tqdm import tqdm

from resources.collections import COLL_FILE_PAIR, parse_collection

from .action import resolve_resource_dir, seed_collection


async def seed_text(collections: str):
    """
    Seed collection tables, from text files with format:
    Simplified # Traditional

    :param collections:
        The collection name separated by comma, see help.
        e.g. hsk1,hsk2
    """

    collections = [x.strip() for x in collections.split(",")]
    try:
        for coll in collections:
            validate_collection_file(coll)
    except Exception as e:
        print(f"Error: {e}")
        print_available_collections()
        return

    with tqdm(total=len(collections)) as progress_bar:
        for coll_name in collections:
            progress_bar.set_description(f"Seeding collection {coll_name}")

            name, parsed_collection = parse_collection(coll_name)
            await seed_collection(name, parsed_collection)

            progress_bar.update(1)


def validate_collection_file(collection: str, resource_dir=None) -> None:
    if collection not in COLL_FILE_PAIR:
        raise Exception(f"Collection {collection!r} is not valid")

    resource_dir = resolve_resource_dir(resource_dir)
    filename = os.path.join(resource_dir, COLL_FILE_PAIR[collection][1])
    if not os.path.isfile(filename):
        raise Exception(f"File {filename!r} is not exist")


def print_available_collections() -> None:
    # TODO: Print available collections
    pass
