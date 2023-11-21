import os.path
from dataclasses import dataclass

COLL_FILE_PAIR = {
    "hsk1": ("HSK1", "hsk1.txt"),
    "hsk2": ("HSK2", "hsk2.txt"),
}


@dataclass
class ZHWord:
    zh_sc: str | None
    zh_tc: str | None

    def __post_init__(self):
        if self.zh_sc == "":
            self.zh_sc = None

        if self.zh_tc == "":
            self.zh_tc = None

        if not any([self.zh_sc, self.zh_tc]):
            raise Exception("At least one of `zh_sc` or `zh_tc` must be present")


DELIMITER = "#"


def parse_collection(source: str) -> tuple[str, list[ZHWord]]:
    name, filename = COLL_FILE_PAIR[source]
    filename = os.path.join(os.getcwd(), "resources/collections/source", filename)
    with open(filename, "r") as f:
        words = []
        for word_pair in f.read().splitlines():
            sc, _, tc = [x.strip() for x in word_pair.partition(DELIMITER)]
            words.append(ZHWord(sc, tc))

        return name, words
