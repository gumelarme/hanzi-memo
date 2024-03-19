import math

from tqdm import tqdm

from lipotes.dictionary.tables import Lexeme
from resources.dictionary import Entry, parse_dict


def chunkify(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


async def seed(
    source: str,
    start: int = 0,
    end: int = -1,
    chunk_size: int = 5000,
):
    """
    Seed lexeme, definition, and dictionary table using available dicts

    :param source:
        The dictionary name, for the complete list of available dictionary
        see 'resources/dictionary/source' directory or run:
            piccolo dictionary help
    :param start:
        Seed from the nth chunk of the dict file
    :param end:
        Seed end at the nth chunk of the dict file
    :param chunk_size:
        Size of the bulk insert chunks.
    """

    parsed_dict = parse_dict(source)
    chunks = chunkify(parsed_dict, chunk_size)

    total = math.ceil(len(parsed_dict) / chunk_size)
    start = max(0, start)

    if end == -1:
        end = total
    else:
        end = max(start, end)

    print(f"{source} dictionary total {len(parsed_dict)} rows")
    message = f"Seeding {source} ({start}-{end}) in chunks of {chunk_size}"
    with tqdm(total=(end - start), desc=message) as progress_bar:
        for i, entries in enumerate(chunks):
            if i < start:
                continue

            if i >= end:
                break

            lexemes = Lexeme.insert()
            for entry in entries:
                lex = Lexeme(zh_sc=entry.zh_sc, zh_tc=entry.zh_tc, pinyin=entry.pinyin)
                lexemes.add(lex)

            await lexemes.returning(Lexeme.id).run()
            progress_bar.update(1)
