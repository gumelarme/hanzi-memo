import os

from .base import ZHWord

COLL_FILE_PAIR = {
    "hsk1": ("HSK1", "hsk1.txt"),
    "hsk2": ("HSK2", "hsk2.txt"),
    "hsk3": ("HSK3", "hsk3.txt"),
    "hsk4": ("HSK4", "hsk4.txt"),
    "hsk5": ("HSK5", "hsk5.txt"),
    "hsk6": ("HSK6", "hsk6.txt"),
}

DELIMITER = "#"


def parse_text_collection(source: str) -> tuple[str, list[ZHWord]]:
    name, filename = COLL_FILE_PAIR[source]
    filename = os.path.join(os.getcwd(), "resources/collections/data/source", filename)
    with open(filename, "r") as f:
        words = []
        for word_pair in f.read().splitlines():
            sc, _, tc = [x.strip() for x in word_pair.partition(DELIMITER)]
            words.append(ZHWord(sc, tc))

        return name, words
