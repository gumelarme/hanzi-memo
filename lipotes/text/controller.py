from litestar import Controller, get
from litestar.contrib.piccolo import PiccoloDTO
from litestar.exceptions import NotFoundException

from lipotes.text.tables import Text


class TextController(Controller):
    path = "/texts"
    return_dto = PiccoloDTO[Text]

    @get("/")
    async def get_texts(self) -> list[Text]:
        result = await Text.objects().limit(10).order_by(Text.id, ascending=False)
        return result

    @get("/{text_id:int}")
    async def get_text_by_id(self, text_id: int) -> Text:
        result = await Text.objects().get(Text.id == text_id)
        if result is None:
            raise NotFoundException()
        return result
