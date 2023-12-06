import os
from xml.etree import ElementTree

from . import ZHWord


def normalize_pinyin(pinyin: str):
    umlaut_u = {
        "Ü": "V",
        "ü": "v",
        "/": "",
    }

    for k, v in umlaut_u.items():
        pinyin = pinyin.replace(k, v)

    return pinyin


def parse_pleco(filename: str) -> dict[str, set[ZHWord]]:
    filename = os.path.join(os.getcwd(), "resources/collections/data/source", filename)

    tree = ElementTree.parse(filename)
    root = tree.getroot()

    categories = {x.attrib["category"] for x in root.findall(".//catassign")}
    print(f"Found {len(categories)} {categories=}")

    collection: dict[str, set[ZHWord]] = {}
    for card in root.findall(".//card"):
        entry = card.find(".//entry")

        def hw_path(x):
            return f".//headword[@charset='{x}']"

        pinyin = entry.find(".//pron[@type='hypy']").text

        try:
            sc = entry.find(hw_path("sc")).text
            tc = entry.find(hw_path("tc")).text
        except AttributeError:
            sc = entry.find(".//headword").text
            tc = sc

        word = ZHWord(
            zh_sc=sc,
            zh_tc=tc,
            pinyin=normalize_pinyin(pinyin),
        )

        for category in card.findall(".//catassign"):
            cat_name = category.attrib["category"]
            if cat_name not in collection:
                collection[cat_name] = set()
            collection[cat_name].add(word)

    return collection
