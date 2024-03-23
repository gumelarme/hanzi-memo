from litestar import Controller, get
from litestar.contrib.piccolo import PiccoloDTO

from lipotes.dictionary.tables import Dictionary


class DictionaryController(Controller):
    path = "/dicts"
    return_dto = PiccoloDTO[Dictionary]

    @get("/")
    async def get_dictionaries(self) -> list[Dictionary]:
        return await Dictionary.objects().limit(10)
