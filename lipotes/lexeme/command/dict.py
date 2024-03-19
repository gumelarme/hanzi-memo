from resources.dictionary.parse import PARSER_FILE_PAIR

# TODO: implement command that download dicts


def list_dict():
    print("Available dicts:")
    dicts = [f"  - {x}" for x in PARSER_FILE_PAIR.keys()]
    print("\n".join(dicts))
