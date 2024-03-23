from tqdm import tqdm

from lipotes.text.parser import parse_text
from lipotes.text.tables import Text


async def seed_text(file: str):
    """
    :param file:
        The yaml file name, in format:
        - title: Something
          text: The text
    """

    bulk_insert = Text.insert()
    for title, text in tqdm(parse_text(file), desc="Seeding text"):
        bulk_insert.add(Text(title=title, text=text))
    await bulk_insert.run()
