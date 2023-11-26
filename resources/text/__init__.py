import os

import yaml

TEXT_FILE_PAIR = {"demo": "demo.yaml"}


def parse_text(source: str) -> list[tuple[str, str]]:
    filename = TEXT_FILE_PAIR[source]

    texts = []
    filename = os.path.join(os.getcwd(), "resources/text/source", filename)
    with open(filename, "r") as file:
        for data in yaml.safe_load(file):
            texts.append((data["title"], data["text"]))

    return texts
