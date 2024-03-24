from litestar import get

from lipotes.collection.controller import CollectionController
from lipotes.dictionary.controller import DictionaryController
from lipotes.dictionary.controller.lexeme import LexemeController
from lipotes.text.controller import TextController


@get("/")
async def index() -> dict[str, any]:
    return {"data": "Hello, this is lipotes"}


api = [
    index,
    TextController,
    DictionaryController,
    CollectionController,
    LexemeController,
]
